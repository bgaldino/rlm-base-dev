# Multi-Shape Rating Data Architecture

**Status**: Design Investigation — For Review
**Scope**: `qb-rating` and `qb-rates` SFDMU data plans
**Related**: `docs/references/sfdmu-composite-key-optimizations.md`, `datasets/sfdmu/qb/en-US/qb-rating/README.md`

---

## Problem Statement

The current `qb-rating` and `qb-rates` data plans use `Insert + deleteOldData: true` (no WHERE clause) for `ProductUsageResource` (PUR), `ProductUsageResourcePolicy` (PURP), and `ProductUsageGrant` (PUG). This is a **shape-exclusive** pattern: each plan run deletes *all* records of each type and re-inserts only what the plan's CSVs contain.

This works correctly for a single, canonical data shape but breaks down when:

- A second product family needs its own rating configuration on the same org
- A downstream CCI project (customer implementation) needs to layer custom rating data on top of the base
- Multiple environments need to manage distinct subsets of rating records independently

Any re-run of one shape's plan wipes all other shapes' records. **The current approach cannot support more than one data shape per org.**

### Requirements

1. **Multi-shape coexistence** — Any number of data shapes can be loaded on the same org without shapes overwriting each other. Each shape is independently loadable and re-runnable.
2. **Drift capture per shape** — Extract modifications made to an org's records and identify drift against the shape's source CSVs, even when multiple shapes coexist.
3. **Test and approval workflow** — Diff extracted state against the baseline, review, then decide:
   - **Merge into base**: update source CSVs and commit to the base plan.
   - **Configure as downstream overlay**: keep the base unchanged; the custom shape lives in a child CCI project.
4. **CCI overlay pattern** — Downstream CCI projects can define their own shape plans that load independently alongside the base without conflict.

---

## Confirmed Constraints

The following constraints are fixed and must be respected by any solution:

1. **No custom fields on PUR, PURP, or PUG.** Custom field deployment on these API 260 SObjects is not permitted. This eliminates any approach that relies on a custom external ID field (e.g., `DataKey__c`) to drive Upsert matching.

2. **No static WHERE clauses.** Hardcoded product SKU lists (e.g., `WHERE Product.StockKeepingUnit IN ('QB-DB', 'QB-DB-TOKEN')`) are not acceptable. As products are added or removed from a shape's CSVs, the WHERE must adapt automatically. Any WHERE-scoped approach must derive its scope dynamically from the plan's own CSV contents at runtime.

---

## Why Upsert Is the Right Model

The shape-exclusive problem exists because `deleteOldData` asserts total ownership of an object type. The correct multi-shape primitive is **Upsert**: each record is independently addressable by a stable key, and a shape's plan can run without touching sibling shapes' records.

Upsert also eliminates the secondary problem of re-runs: instead of wipe-and-reload, each run updates records in place (matched by key) and inserts only net-new records. Records removed from a shape's CSVs are left in place until explicitly deleted — which is now a feature, since sibling shapes' records are never accidentally removed.

### Why Upsert Is Currently Broken (SFDMU v5)

Two confirmed SFDMU v5 bugs block native Upsert for these objects:

**Bug 2 — TARGET SELECT SOQL injection (2-hop traversal columns)**
When building the Upsert TARGET SELECT query, SFDMU strips the first-hop prefix from 2-hop traversal columns included in the SOQL SELECT (e.g., `ProductUsageResource.Product.StockKeepingUnit` becomes `Product.StockKeepingUnit` — not a valid field on `ProductUsageResourcePolicy`). This produces invalid SOQL and fails the Upsert.

**Bug 3 — Traversal externalId components never match existing records**
When `externalId` contains relationship-traversal components (even 1-hop, e.g., `Product.StockKeepingUnit;UsageResource.Code`), SFDMU v5 always inserts instead of updating. Records in the org are never matched; every re-run creates duplicates.

| Object | Affected by Bug 2 | Affected by Bug 3 |
|--------|-------------------|-------------------|
| **PUR** | No (only 1-hop traversals in SELECT) | Yes — externalId is `Product.StockKeepingUnit;UsageResource.Code` |
| **PURP** | Yes — SELECT includes 2-hop `ProductUsageResource.Product.StockKeepingUnit` | No — externalId is `ProductUsageResourceId` (direct field) |
| **PUG** | Yes — SELECT includes 2-hop `ProductUsageResource.Product.StockKeepingUnit` | Yes — externalId components are all 1-hop traversals |

Because custom fields are not permitted, these bugs cannot be bypassed by introducing a custom direct-field externalId. Two approaches remain viable: one that works around the bugs by adding WHERE-scoped shape isolation (Option A), and one that bypasses SFDMU's externalId system entirely via pre-ID resolution (Option B).

---

## Option A — Dynamic WHERE + Insert + deleteOldData

### Concept

Keep `Insert + deleteOldData` as the SFDMU operation, but scope each plan's DELETE to only the records it owns. The scope is derived dynamically from the plan's own CSV files at runtime — never hardcoded — so it automatically reflects whatever products are currently in the shape.

### How the Dynamic WHERE Is Generated

The `LoadSFDMUData` CCI wrapper task (`tasks/rlm_sfdmu.py`) already modifies a working copy of `export.json` before running SFDMU (it injects org credentials into the `orgs` block). The same mechanism would:

1. Scan the plan's PUR CSV for all unique `Product.StockKeepingUnit` values.
2. Construct a WHERE clause from that exact set.
3. Inject the WHERE into each relevant query in the working copy of `export.json`.
4. Run SFDMU — `deleteOldData` now only deletes records whose products are in the plan's CSV.

```
PUR:  WHERE Product.StockKeepingUnit IN ('QB-DB', 'QB-CMT-TKN-EACH', ...)
PURP: WHERE ProductUsageResource.Product.StockKeepingUnit IN ('QB-DB', 'QB-CMT-TKN-EACH', ...)
PUG:  WHERE UsageDefinitionProduct.StockKeepingUnit IN ('QB-DB-TOKEN', ...)
```

The WHERE is always derived from the plan's data, so adding or removing a product from the CSV automatically adjusts the scope on the next run.

### Shape Isolation

Each shape plan (base or downstream overlay) scans its own CSVs and generates its own WHERE. Shape A's plan only deletes Shape A's products' records; Shape B's plan only deletes Shape B's products' records. Provided shapes have disjoint product sets, they are completely independent.

### Drift Capture

Extraction uses the same dynamically derived WHERE clause. Only the shape's records are returned; the diff is naturally shape-scoped.

### Active Record Limitation

The Active record deletion conflict still applies. SFDMU's `deleteOldData` sends a direct REST DELETE. Salesforce rejects deletion of Active PURs and PUGs — the entire batch fails, leaving Active records in place while new Draft records are inserted on top. The Apex cleanup scripts (`delete_qb_rating_data`, `delete_qb_rates_data`) must deactivate and delete the shape's records before a plan re-run that includes `deleteOldData`.

In a multi-shape environment, the cleanup scripts would need to be scoped to only deactivate and delete the shape's products' records — currently they delete all records of each type.

### Pros
- Works within SFDMU's existing architecture — no new SFDMU capabilities needed
- No custom fields required
- WHERE is always in sync with the plan's CSVs — no manual maintenance
- Shapes with disjoint product sets are completely isolated
- Drift extraction naturally scoped by the same WHERE
- CCI overlay: downstream project defines its own shape plan, generates its own WHERE

### Cons
- Still wipe-and-reload per shape — re-runs delete all of a shape's records and re-insert from CSV
- Shapes **must have disjoint product sets** — if two shapes share a `Product2` record, they cannot independently manage PURs for it
- The PURP WHERE (`ProductUsageResource.Product.StockKeepingUnit IN (...)`) is a 2-hop traversal from PURP. Whether Salesforce resolves this in the DELETE context needs verification (see Investigation Plan)
- Apex cleanup scripts must be refactored to scope deactivation/deletion to only the shape's products

---

## Option B — Pre-ID Resolution → True Upsert

### Concept

Bypass SFDMU's externalId traversal matching entirely. Before running SFDMU, a pre-resolution CCI task queries the org to retrieve Salesforce record IDs for all existing PURs, PURPs, and PUGs using their natural keys (traversal fields). It then merges those IDs into working copies of the plan CSVs. SFDMU then runs `Update` for records that have IDs (already exist in org) and `Insert` for records without IDs (net-new). `deleteOldData` is not used.

```
Pre-resolution task:
  1. Query org:
       SELECT Id, Product.StockKeepingUnit, UsageResource.Code
       FROM ProductUsageResource
  2. Build map: "QB-DB:UR-CPUTIME" → "a0x000..."
  3. Walk plan CSV rows, match by natural key, write Id into working CSV copy

SFDMU (on working CSV with Ids populated):
  - Records with Id: operation = Update (matches on Id — direct field, no traversal)
  - Records without Id: operation = Insert
  - No deleteOldData
```

`Id` is a direct field on every SObject — SFDMU's Upsert using `externalId: Id` avoids Bugs 2 and 3 entirely. Alternatively, the pre-resolution task can split the working CSV into two files (matched and unmatched) and run two SFDMU passes.

### Shape Isolation

Shapes are isolated by construction: each shape's plan only includes its own records in its CSVs. The pre-resolution step only looks up IDs for the records in the plan's CSVs. Records belonging to other shapes are never read, updated, or deleted.

### Record Removal

Upsert never deletes. Records removed from a shape's CSVs remain in the org until explicitly removed. This requires a complementary removal strategy:
- The pre-resolution task can identify records present in the org (for this shape's product set) but absent from the plan CSVs — surfacing them as drift candidates for review.
- Approved removals trigger a targeted Apex delete or a SFDMU `Delete` pass scoped to those specific record IDs.

### Drift Capture

The pre-resolution task's org query naturally returns all records for the shape's products, including any that were modified directly in the org. Comparing this against the plan CSVs produces the full drift picture: modified fields, added records, and removed records — all without any WHERE clause.

### Active Record Handling

No `deleteOldData` means no Active record deletion conflict. Update operations on Active PURs/PUGs update their non-status fields in place. Activation state is managed separately (as it is today, via Apex). Re-runs are safe regardless of the Active/Draft state of existing records.

### Pros
- True Upsert — existing records updated in place, new records inserted, no wipe-and-reload
- No custom fields required
- No SFDMU traversal bug exposure (matching is on `Id`, a direct field)
- Shapes with shared products can coexist — each shape's records are independently addressable by their Salesforce IDs
- Active record conflict is eliminated
- Drift capture is comprehensive and requires no WHERE scoping
- Record removal is explicit and approval-gated

### Cons
- Requires a new pre-resolution CCI task (Python, using CCI's Salesforce API client)
- Two-pass SFDMU execution (Update pass + Insert pass) adds complexity
- The pre-resolution task must correctly map all three objects (PUR, PURP, PUG) and handle the FK chain: PURP's ID lookup requires knowing its PUR's ID; PUG's ID lookup requires knowing its PUR's ID
- Removed records are not automatically cleaned up — requires a defined approval and deletion workflow
- More moving parts than Option A — more to test and maintain

---

## Option C — Multi-Pass objectSets with useSeparatedCSVFiles (Structural Pattern)

`useSeparatedCSVFiles: true` with multiple `objectSets` provides clean file organization and per-shape CSV isolation. It does not independently solve the Upsert or shape isolation problem, but it pairs well with either Option A or Option B:

- **With Option A**: each shape is its own objectSet, reading from its own subdirectory, with dynamically injected WHERE clauses.
- **With Option B**: each shape's CSVs live in a subdirectory; the pre-resolution task operates on the objectSet's subdirectory; extraction outputs are also per-objectSet.
- **Pre/post passes**: objectSets already sequence deactivation → data load → activation. Multi-shape adds a shape-scoped cleanup pass before each shape's data pass.

Include this pattern in whichever option is chosen; it is an organizational enhancement, not a standalone solution.

---

## Investigation Plan

Before committing to either option, the following investigations should be conducted in sequence. Each investigation has a clear pass/fail outcome that determines the path forward.

### Investigation 1 — SOQL Validity of 2-hop Traversal WHERE on PURP (Blocker for Option A)

**Question**: Does the Salesforce platform resolve a 2-hop traversal in a SOQL WHERE clause on `ProductUsageResourcePolicy`?

**Test**:
```sql
SELECT Id FROM ProductUsageResourcePolicy
WHERE ProductUsageResource.Product.StockKeepingUnit IN ('QB-DB')
```
Run this query against any org with PURP records using Salesforce CLI (`sf data query`) or Developer Console.

**Pass**: Query returns records (platform resolves the 2-hop traversal in WHERE).
**Fail**: Query throws `INVALID_FIELD` or `Didn't understand relationship` error.

**Impact**:
- **Pass** → Option A is viable for PURP. Proceed to Investigation 2.
- **Fail** → Option A cannot scope PURP deletion. The dynamic WHERE would work for PUR but not PURP. Option A is partially broken; Option B becomes the only path to full shape isolation.

---

### Investigation 2 — SFDMU deleteOldData Respects WHERE Clause

**Question**: Does SFDMU's `deleteOldData: true` actually restrict its DELETE to records matching the query's WHERE clause, or does it delete all records of the type?

**Test**:
Set up a plan with a WHERE-scoped PUR query on a sandbox org that has PURs for multiple products. Set `deleteOldData: true`. Run the plan. Verify that only the WHERE-matching PURs are deleted.

**Tools**: Before/after record counts using `sf data query` or a CCI count task.

**Pass**: Only the WHERE-matching records are deleted. Other PURs survive.
**Fail**: All PURs are deleted regardless of WHERE.

**Impact**:
- **Pass** → Dynamic WHERE scoping works in SFDMU. Proceed to Investigation 3.
- **Fail** → SFDMU's `deleteOldData` ignores WHERE — Option A is not viable at all. Option B is the only remaining path.

---

### Investigation 3 — Dynamic WHERE Injection Feasibility

**Question**: Can the `LoadSFDMUData` wrapper task reliably derive a WHERE clause from the plan's CSV files and inject it into the working `export.json` before SFDMU runs?

**Test**: Prototype the injection logic in `tasks/rlm_sfdmu.py`:
1. Parse the PUR CSV → extract unique `Product.StockKeepingUnit` values.
2. Construct `WHERE Product.StockKeepingUnit IN ('SKU1', 'SKU2', ...)`.
3. Inject into the PUR, PURP, and PUG queries in a copy of `export.json`.
4. Log the modified queries and confirm they are syntactically valid SOQL.

**Also test**: Edge cases — empty product set (all products removed from CSV), single product, and a very large set (IN clause length limits in SOQL: 1,000 items max for SOQL IN clauses on most contexts).

**Pass**: Injection produces valid SOQL for all three objects; SFDMU runs successfully with injected WHERE.
**Fail**: Injection produces invalid SOQL, or SFDMU fails to parse the modified `export.json`.

**Impact**: If Investigation 1 and 2 both pass, this is an implementation task, not a blocker. If it fails on edge cases, define fallback behavior (e.g., batch the IN clause into multiple queries for large shapes).

---

### Investigation 4 — Pre-ID Resolution Query Feasibility (Required for Option B)

**Question**: Can the natural keys for PUR, PURP, and PUG be reliably reconstructed from org queries to build an ID map?

**Tests** (run against an org with all three objects populated):

```sql
-- PUR: natural key is Product SKU + UsageResource Code
SELECT Id, Product.StockKeepingUnit, UsageResource.Code
FROM ProductUsageResource

-- PURP: natural key inherits from its PUR (1:1 relationship)
SELECT Id, ProductUsageResourceId,
       ProductUsageResource.Product.StockKeepingUnit,
       ProductUsageResource.UsageResource.Code
FROM ProductUsageResourcePolicy

-- PUG: natural key is UsageDefinitionProduct SKU + UoMClass Code + UoM Code
SELECT Id, UsageDefinitionProduct.StockKeepingUnit,
       UnitOfMeasureClass.Code, UnitOfMeasure.UnitCode
FROM ProductUsageGrant
```

**Pass**: All three queries return traversal-field values alongside `Id`. The natural keys are unique per record and match the keys in the plan CSVs.
**Fail**: Traversal fields return null, the natural keys are non-unique, or the queries fail.

**Impact**:
- **Pass** → Option B pre-resolution is feasible. Proceed to Investigation 5.
- **Fail** → Identify which object fails and why. A fallback for PURP (which has a 1:1 with PUR) is to resolve its ID via PUR's ID from the PUR map rather than a direct query.

---

### Investigation 5 — SFDMU Upsert with `externalId: Id` (Option B)

**Question**: Does SFDMU correctly process a CSV that has `Id` populated for existing records and empty for new records, using `operation: Upsert` and `externalId: Id`?

**Alternative**: Does SFDMU support running two passes within one objectSet — one `Update` pass (for rows with `Id`) and one `Insert` pass (for rows without `Id`)?

**Test**: Prepare a working CSV with `Id` populated for half the records (simulating matched existing records). Run SFDMU with `operation: Upsert` and `externalId: Id`. Verify that matched records are updated and unmatched records are inserted.

**Pass**: SFDMU correctly routes rows with `Id` to Update and rows without `Id` to Insert.
**Fail**: SFDMU fails on rows with empty `Id`, or treats all rows as Insert.

**Impact**:
- **Pass** → Single SFDMU pass with `externalId: Id` is the simplest implementation path for Option B.
- **Fail** → Two-pass approach: pre-resolution task splits the CSV into `_update.csv` (has `Id`) and `_insert.csv` (no `Id`), with two separate SFDMU passes per object.

---

### Investigation 6 — Multi-Shape Coexistence End-to-End Test

**Question**: With either Option A or Option B implemented, do two shapes truly coexist without interfering?

**Test sequence**:
1. Load Shape A (e.g., QB-DB + QB-DB-TOKEN products) using the new multi-shape plan.
2. Record counts: PUR_A, PURP_A, PUG_A.
3. Load Shape B (e.g., QB-CMT-TKN-* products) using its own shape plan.
4. Record counts: PUR_A+B, PURP_A+B, PUG_A+B.
5. Re-run Shape A plan.
6. Record counts again. Verify: Shape A counts unchanged, Shape B counts unchanged.
7. Re-run Shape B plan.
8. Verify: Shape A and Shape B counts both still correct.

**Pass**: All counts correct after each step. No cross-shape pollution.
**Fail**: Re-running one shape deletes or duplicates the other shape's records.

---

## Decision Matrix

| Criterion | Option A (Dynamic WHERE) | Option B (Pre-ID Resolution) |
|-----------|-------------------------|------------------------------|
| Requires custom fields | No | No |
| Works without SFDMU bug fixes | Yes | Yes |
| True Upsert (no wipe-and-reload per shape) | No | Yes |
| Shapes can share Product2 records | No | Yes |
| Active record conflict eliminated | No — Apex cleanup still required before re-run | Yes — Update works on Active records |
| Drift capture per shape | Yes (WHERE-derived from CSV) | Yes (query all by natural key, diff against CSV) |
| Record removal approach | Shape re-run (scoped wipe cleans up removed records) | Explicit approval + targeted delete |
| Implementation complexity | Medium (WHERE injection in LoadSFDMUData) | High (new pre-resolution task + two-pass SFDMU) |
| Blocked by Investigation 1 (PURP 2-hop WHERE) | Yes | No |
| Blocked by Investigation 2 (SFDMU deleteOldData WHERE scope) | Yes | No |

---

## Recommended Path

**Start with Investigations 1 and 2** — they are quick (single SOQL query and a one-plan SFDMU test) and are go/no-go gates for Option A. If both pass, Option A is achievable with moderate effort and no new SFDMU capabilities. If either fails, Option B is the only remaining SFDMU-compatible path.

**Run Investigations 4 and 5 in parallel with 1 and 2** — the pre-resolution queries can be validated immediately on any org with data. This gives an early read on Option B feasibility before committing to implementation.

**Decision point after Investigations 1–5**:

```
Inv 1 pass AND Inv 2 pass
  → Option A viable. Implement dynamic WHERE injection.
  → Option B is still preferable long-term (true Upsert, Active record safety,
    shared-product support) but Option A can ship sooner.

Inv 1 fail OR Inv 2 fail
  → Option A not viable. Option B is the path.
  → Prioritize Investigations 4 and 5 to validate Option B fully.

Both options viable
  → Evaluate: are re-runs within a shape expected to be frequent?
    Is per-record update precision needed, or is full shape reload acceptable?
    Shared products between shapes expected?
    If yes to any → Option B. Otherwise → Option A for now, Option B as follow-on.
```

**Investigation 6 is always required** — regardless of which option is chosen, end-to-end multi-shape coexistence must be verified before the approach is considered production-ready.
