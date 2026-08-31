---
name: sfdmu-data-plans
description: >-
  SFDMU v5 data plan authoring and review for Revenue Cloud. Use when creating,
  modifying, or reviewing export.json files, CSV data files, or SFDMU data plans.
  Covers v5 rules, known bugs, externalId patterns, operation selection,
  deleteOldData safety, and cross-plan dependencies.
---

# SFDMU v5 Data Plans

SFDMU v5.6.4+ is required (5.6.4 fixed Upsert matching for relationship-traversal externalIds). v4 syntax is not supported.

## Quick Rules

1. externalId delimiter is `;` — NOT `$$` (that's v4).
2. Relationship-traversal externalId matches under `Upsert` on the 5.6.4+ floor (Bugs 2/3/5 fixed) — the old `Insert` + `deleteOldData: true` workaround is pre-5.6.4. Only Bug 4 (`$$` in lookup reference columns — self-referential *and* cross-object) is still live.
3. Never change Upsert → Insert+deleteOldData without explicit user approval.
4. Empty CSV → set `excluded: true` (prevents destructive wipe). See *Which empty-CSV remedy* — three exist and they are not interchangeable.
5. Parent → child order in `objects` array (deletion runs reverse).
6. `$$` CSV column must match externalId fields exactly.
7. After extraction: run `post_process_extraction.py` to add `$$` columns.
8. **A plan that loads cleanly into a fresh org is not safe to re-run into a *used* org** — check the plan's operations against what the org already has. See *Reloading a plan into a live org*.

## DO NOT

- **DO NOT** use `$$Field1$Field2` syntax in `externalId` (v4, not v5)
- **DO NOT** change `Upsert` to `Insert+deleteOldData` without user approval
- **DO NOT** leave empty CSVs without `excluded: true`
- **DO NOT** use `$$` composite notation for lookup reference columns in CSVs (Bug 4 — self-referential and cross-object `$$` references fail on import; use simple field references)
- **DO NOT** add `Insert` + `deleteOldData: true` for a relationship-traversal externalId citing Bugs 2/3/5 — those are fixed on the 5.6.4+ floor; `Upsert` matches. (Existing plans that still carry that pattern migrate under the gated `sfdmu-v5-optimization` initiative, not ad hoc.)
- **DO NOT** re-run a plan into an org with live transactional data to add one record — see below

## export.json Structure

```json
{
  "apiVersion": "68.0",
  "excludeIdsFromCSVFiles": "true",
  "objectSets": [
    {
      "objects": [
        {
          "query": "SELECT Field1, Field2, LookupId FROM SObject ORDER BY Field1 ASC",
          "operation": "Upsert",
          "externalId": "Field1;Field2",
          "excluded": false
        }
      ]
    }
  ],
  "orgs": []
}
```

## externalId Rules (v5)

- Use `;` delimiters: `Field1;Field2` (NOT `$$Field1$Field2` — that is v4 syntax)
- `$$` composite key columns in CSVs are still valid for source-record matching
- Relationship traversals in externalId: `Parent.Field` (1-hop), `GrandParent.Parent.Field` (2-hop)

## Operation Selection Guide

| Situation | Operation | deleteOldData | Why |
|-----------|-----------|---------------|-----|
| Has a direct unique field (Name, Code, etc.) | `Upsert` | `false` | Safe matching on direct fields |
| Composite uniqueness, all direct fields | `Upsert` | `false` | `$$` column in CSV enables matching |
| externalId uses any relationship traversal | `Upsert` | `false` | 5.6.4+ matches on traversals (Bugs 3/5 fixed); `Insert`+`deleteOldData` was the pre-5.6.4 workaround |
| Auto-number Name + all-relationship externalId | `Upsert` | `false` | 5.6.4+ matches on the traversal externalId (Bugs 3/5 fixed) — the auto-number Name is not the match key |
| Read-only reference (already loaded by another plan) | `Readonly` | `false` | Just resolves IDs for child lookups |
| Updating existing records (set fields) | `Update` | `false` | Only modifies matched records |
| Empty CSV (no records yet) | mark `excluded: true` | — | Prevents destructive delete-on-load |

## Bug 4 — `$$` Composite Notation Fails for Lookup Reference Columns (self-referential and cross-object)

**Problem:** When an object has a self-referential lookup (e.g., `ProductComponentGroup.ParentGroupId` → `ProductComponentGroup`) and the CSV uses `$$` composite key notation for that reference (e.g., `ParentGroup.$$Code$ParentProduct.StockKeepingUnit`), SFDMU cannot resolve the parent record. The MissingParentRecordsReport shows anonymized hashes instead of matched records, and the lookup fields are left null after import — even though the parent records exist and SFDMU runs multiple passes.

**Root cause:** SFDMU's `$$` composite notation works for the *primary* record's externalId matching (source↔target), but fails when used as a *lookup reference column* — for **self-referential and cross-object** relationships alike. SFDMU cannot decompose a composite `$$` value back into individual fields to find the referenced record.

**Fix:** Use simple single-field references for self-referential lookups:
- Change `ParentGroup.$$Code$ParentProduct.StockKeepingUnit` → `ParentGroup.Code`
- Ensure the `externalId` for the object is the simple field (e.g., `Code`) — not a composite
- This works when the simple field is unique (or unique within the context of the plan)

**Example (ProductComponentGroup):**
```
# BROKEN — ParentGroup reference uses $$ composite, SFDMU cannot resolve
Header: $$Code$ParentProduct.StockKeepingUnit,...,ParentGroup.$$Code$ParentProduct.StockKeepingUnit
Value:  Cooling;QB-QRack-750,...,Computing;QB-QRack-750
externalId: "Code;ParentProduct.StockKeepingUnit"

# WORKS — ParentGroup reference uses simple field
Header: Code,...,ParentGroup.Code
Value:  Cooling,...,Computing
externalId: "Code"
```

**Audit required:** Review all data plans that use `$$` composite columns as *lookup references* (not just primary keys). Cross-object `$$` references (e.g., `ProductComponentGroup.$$Code$...` referenced from `ProductRelatedComponent`) fail the same way as self-references — SFDMU cannot decompose a composite `$$` value in **any** lookup-reference column. **Fix (both cases):** use a simple single-field reference for the lookup column.

## v5 Bugs — one live on the 5.6.4 floor, four fixed upstream

With **v5.6.4+ as the required floor**, the historical Upsert-matching bugs are
fixed and **only Bug 4 is still live**. On a 5.6.4+ plugin, author traversal
externalId plans as `Upsert` — do not add `Insert` + `deleteOldData: true`
citing Bugs 1/2/3/5. (See the dedicated **Bug 4** section above for the one live
case; existing plans still carrying Insert+deleteOldData migrate under the gated
`sfdmu-v5-optimization` initiative.)

<details>
<summary>Bugs 1/2/3/5 — fixed at or below the 5.6.4 floor (history; do NOT apply their workarounds on 5.6.4+)</summary>

- **Bug 1 — all-multi-hop externalId fails validation** (`{Object} has no mandatory external Id field definition`). **Fixed in 5.3.1.** *Was:* include at least one direct field in externalId.
- **Bug 2 — 2-hop traversal columns produce malformed SOQL in the Upsert TARGET SELECT.** **Fixed in 5.6.3.** *Was:* `Insert` + `deleteOldData: true`. *Residue by design:* dotted composite segments are still dropped from child `__r` queries on **extract** (the `#N/A` blanking that `post_process_extraction.py` backfills; 5.6.3 also set `#N/A` = null marker, bare `N/A` = literal).
- **Bug 3 — Upsert with relationship-traversal externalId never matches** (duplicates every run, even 1-hop). **Fixed in the 5.6.4 release** (commit `50be987`, `_getNestedRecordFieldValue`; source-verified). *Was:* `Insert` + `deleteOldData: true`.
- **Bug 5 — composite externalId of all relationship traversals fails upsert matching.** **Fixed in 5.6.4** (same relationship-path matching fix). *Was:* prefer a direct-field externalId, else `Insert` + `deleteOldData: true` after approval.

</details>

## CRITICAL — Insert + deleteOldData Safety

**Never change Upsert to Insert + deleteOldData without:**
1. Explaining which *current* reason makes Upsert impossible (on the 5.6.4+ floor Bugs 1/2/3/5 are fixed — not those historical bugs)
2. Confirming no direct-field externalId alternative exists
3. Getting explicit user approval

`deleteOldData: true` deletes ALL existing records before inserting. Misapplied, it wipes data that Upsert would have safely matched.

## Reloading a Plan Into a Live Org

Plans are written for a **fresh org**. Re-running one into an org that already has
assets, entitlements, or other transactional data can duplicate or fail — and the
failure mode differs by operation. Check before re-running:

| Operation | Re-run into a used org |
|-----------|------------------------|
| `Upsert` / `Update` | ✅ No duplicates — matches on externalId (qb-pcm, qb-billing, qb-tax). ⚠️ Not the same as "the change applies": objects carrying `skipExistingRecords: true` (all the qb-billing billing objects) skip matched rows entirely, so a **correction** to existing data silently does not land. |
| `Insert`, **no** `deleteOldData` | ⛔ **Duplicates every row.** No matching happens at all. |
| `Insert` + `deleteOldData: true` | ⛔ Blocked when live records reference the design-time rows it must delete first |

Two concrete traps in the QB plans:

- **`qb-pricing` inserts `PricebookEntry` with no `deleteOldData`** — re-running the
  **task** (`insert_quantumbit_pricing_data`) on its own duplicates every entry. The
  **flow** is safe: `prepare_pricing_data` runs `delete_quantumbit_pricing_data`
  first, which clears every Insert-operation object in the plan. So reach for the
  flow, or run the delete task yourself before the insert.
- **`qb-rating` / `qb-rates` use `Insert` + `deleteOldData`** — which cannot clear
  design-time rows (PUR/PUG/RateCardEntry, and `AssetRateCardEntry` referencing
  `RateCardEntry`) while live entitlements point at them. The delete silently leaves
  them and you get a duplicate Draft set.

**To add one product to a live org, load it surgically** — insert just the new
records and their relationships (a throwaway script or anonymous Apex), rather than
re-running the plan. Then:

1. **Still commit the new rows to the plan CSVs** so a *fresh* build picks them up.
2. Update the plan README and re-run `check_plan_readme_consistency.py --strict`.
3. **Verify plan-level wiring on the next full `prepare_rlm_org` build** — a
   surgical load proves the *records* work, not that the *plan* creates them
   correctly. Track that verification as owed work until it runs.

## Object Ordering

Objects in the `objects` array must be ordered **parent → child**. SFDMU deletes `deleteOldData: true` objects in **reverse array order** (last deleted first), so parent-first ordering ensures child records are deleted before parents.

## SOQL Query Rules

- ORDER BY fields must appear in the SELECT clause
- Relationship traversal columns in SOQL must match CSV header expectations
- Use relationship notation for lookup references: `Parent.Field` not `ParentId`

## CSV Conventions

- `$$` composite key columns: header format `$$Field1$Parent.Field2` — values must match exactly
- Empty CSVs: must have `excluded: true` in export.json to prevent destructive delete
- After extraction, run `scripts/post_process_extraction.py` to add `$$` columns (SFDMU v5 doesn't write them during extraction)

## Self-Lookup Edge Case (Generic)

For self-referential lookups (`Object.LookupToSameObject__c`), updates may be skipped when
the plan uses only traversal columns (`LookupToSameObject__r.Name`) in an `Update` pass.
SFDMU can reduce runtime source columns and treat rows as unchanged.

### Proven Working Pattern

For the update pass, include BOTH:
- the lookup ID field(s) (`LookupToSameObject__c`)
- the traversal reference field(s) (`LookupToSameObject__r.<ExternalIdField>`)

This combination helps SFDMU compute deltas and apply updates reliably for
self-referential lookups.

Example (Account self-lookups):
- `RLM_Primary_Distributor__c` + `RLM_Primary_Distributor__r.Name`
- `RLM_Primary_Reseller__c` + `RLM_Primary_Reseller__r.Name`

### Diagnostics

If lookup updates are unexpectedly skipped:
1. Check `source/*_source.csv` after a run. If expected lookup columns are missing there,
   SFDMU dropped them before processing.
2. Run with `simulation: true` to inspect pass-level behavior safely.
3. Compare SOURCE/TARGET query lines in task logs to confirm the effective field list.

### Related SFDMU Docs

- Basic examples (self-reference / circular references): https://help.sfdmu.com/examples/basic-examples
- Fields Mapping: https://help.sfdmu.com/full-documentation/advanced-features/fields-mapping
  - Important: field mapping applies only to direct fields and does not extend to
    reference-traversal query fields.

## Multi-Pass Architecture

Some plans use multiple objectSets (passes) to handle circular dependencies or activation ordering:
- **Pass 1**: Insert records in Draft/Inactive status
- **Pass 2**: Update records to Active status (after dependencies exist)
- **Pass 3**: Set cross-references that require both ends to exist

Example: `qb-billing` uses 3 passes: draft insert → activate treatment items → activate treatments and set BillingPolicy.DefaultBillingTreatmentId.

## Review Checklist

- [ ] externalId uses `;` delimiters (not `$$`)
- [ ] Relationship-traversal externalId uses `operation: Upsert` (matches on the 5.6.4+ floor — do NOT add Insert+deleteOldData citing Bugs 2/3/5)
- [ ] ORDER BY fields present in SELECT clause
- [ ] Relationship traversal columns in SOQL match CSV headers
- [ ] Empty CSVs have `excluded: true`
- [ ] Objects ordered parent → child
- [ ] `$$` composite key CSV headers match externalId fields exactly
- [ ] `deleteOldData: true` only where a concrete *current* reason applies + user approval (Bugs 1/2/3/5 are fixed on 5.6.4+ — not justifications)
- [ ] No `$$` composite notation used for lookup reference columns (Bug 4 — use simple field references instead)
- [ ] Self-referential lookups use simple field references (e.g., `ParentGroup.Code` not `ParentGroup.$$Code$...`)
- [ ] All-traversal externalIds use `Upsert` on the 5.6.4+ floor (Bugs 3/5 fixed); any residual `Insert` + `deleteOldData: true` is a pre-5.6.4 plan awaiting the gated `sfdmu-v5-optimization` migration

## Where a plan's CSVs live

Two locations, and which one a plan owes a file in depends on the **pass**, not on the object:

| Location | Read when |
|----------|-----------|
| `<plan>/<Object>.csv` | the default for any pass that writes the object from a file |
| `<plan>/objectset_source/object-set-N/<Object>.csv` | overrides the root file **for pass N only**, and only when the plan's top-level `useSeparatedCSVFiles` is `true` (`object-set-N` is 1-based; pass indexes are 0-based) |

Two prerequisites, not one. `useSeparatedCSVFiles: true` at the plan's top level is what makes SFDMU
substitute `objectset_source/object-set-N/` at all — without it, every pass reads the plan root
regardless of what that directory holds, so a plan whose only CSV for an object lives under
`object-set-2/` and never sets the flag silently never loads it. And even with the flag set, pass 1
is never substituted: `Script.ts`'s `rawSourceDirectoryPath` returns the plan root whenever
`objectSetIndex` is falsy (index 0), flag or no flag — `object-set-1/` becomes readable only through
this repo's opt-in `sync_objectset_source_to_source` step, which copies it onto the root before SFDMU
runs. `_objects_owing_root_csv` checks the flag before crediting a pass-2+ override as coverage.

An object declared in several passes needs a file for **each** writable pass. `BillingPolicy` in
`qb-billing` is `Upsert` in pass 1 and `Update` in pass 3 with an override for pass 3 only, so it
needs *both* its root CSV and its per-pass one — 16 objects across 7 plans have that shape. A CSV
placed in an `object-set-N/` whose pass does not declare the object is **never read**; the validator
reports it (High) rather than loading it.

Two shapes owe no root CSV at all:

- **no live writable declaration in any pass** — `excluded: true`, plain `Delete`, and `Readonly`
  are all source-free, for different reasons: an `excluded` declaration is skipped entirely; a
  `Delete` one is skipped by the exact same runtime gate as `Readonly`
  (`MigrationJobTask.updateRecordsAsync`'s early return for `operation === Readonly ||
  === Delete`, verified against the installed `sfdmu@5.8.0` source); and a `Readonly` one is
  queried from the *target org* instead. None of the three ever reads a source file, and a mix
  across passes counts too — an object `excluded` in pass 1 and `Delete` in pass 2 still owes
  nothing. Do not add an empty CSV to satisfy a checker. **The `Readonly` case is verified live,
  not inferred**,
  because the inference cuts the other way and a reviewer raised it: every load runs
  `--sourceusername CSVFILE`, so it looks as though a Readonly object's rows must come from a CSV
  too. They do not. `procedure-plans` declares `ExpressionSetDefinition` as `Readonly` with **no
  CSV at either location**, while `ProcedurePlanOption.csv` traverses it
  (`ExpressionSetDefinition.DeveloperName`) — and `ProcedurePlanOption.ExpressionSetDefinitionId`
  is populated with real ids in both fresh 264 orgs. The traversal resolved against the target org
  with no source rows in existence.
  - Corollary worth knowing before you "fix" one: a Readonly CSV that *does* exist, such as
    `inapp/RecordType.csv`, is maintained but not required for resolution. Its README record count
    describes org records rather than file rows — which is exactly how `procedure-plans/README.md`
    documents `ExpressionSetDefinition` (`Readonly`, 2 records, no file). Neither the validator nor
    `check_plan_readme_consistency.py` reports such a file's deletion, and that is correct.
- **every writable pass supplied per-pass** — the root path is an alternative location for the same
  file, not an additional requirement.

`validate_sfdmu_v5_datasets.py` enforces exactly this (`_objects_owing_root_csv`), and
`tests/test_sfdmu_csv_expectation.py` pins both directions. Read the operation from the pass, never
from the merged config: the validator's own `_parse_object_configs` keeps only the **first**
declaration, so an object Readonly or `excluded` in pass 1 and `Upsert` in pass 2 looks exempt when
it is not — SFDMU itself processes each pass independently at runtime.

## Which empty-CSV remedy

A zero-byte or header-only CSV has three possible fixes, and the validator's own message ("Add
header row with fields from query") is only one of them. Pick by *why* the file is empty:

| Situation | Remedy |
|-----------|--------|
| The object should load, but the CSV lost its header | Add the header row — the validator's advice, and the only one that preserves intent |
| The object genuinely has no data for this dataset, in a **wired** plan | `excluded: true` — prevents a destructive wipe on a `deleteOldData` plan, and is why rule 4 exists |
| The whole plan is unwired and unmaintained | Delete the plan — `excluded: true` would make a checker green while leaving a plan nobody loads |

The third row's precedent is `q3-multicurrency`, an unwired plan with zero-byte `CostBook`/
`CostBookEntry` CSVs, resolved by removal in `dab545ab`. `mfg/en-US/mfg-multicurrency` carried the
identical finding (zero-byte `Upsert` CSVs, all unwired) and was removed the same way (pack 110)
rather than `excluded: true`-ing the seven — `excluded: true` **would** have turned the validator
green in one line and matched rule 4's letter, but it changes load semantics on a plan that may
later be wired (an excluded object silently does not load), suppressing the signal rather than
removing its cause.

## Developer scratch area

`datasets/sfdmu/test/` is a developer-local scratch area for experimental and throwaway plans. It is:

- **Gitignored** — `datasets/sfdmu/test/**` in `.gitignore`; never committed or pushed
- **Excluded from validation** — `validate_sfdmu_v5_datasets.py` skips `test/` (and
  `objectset_source/`, `processed/`, `source/`, `logs/`) when *discovering* plans, via
  `_SKIP_SEGMENTS`, plus `*.bak` via a separate suffix branch in `_is_skippable_export` — named
  because grepping `_SKIP_SEGMENTS` for the `.bak` behavior does not find it. Note that `objectset_source/` is skipped only as a plan root: within a plan the
  validator reads it as a first-class CSV location — see *Where a plan's CSVs live*
- **Not referenced** by any shipped task, flow, CI job, or test

To clean up local scratch plans: `rm -rf datasets/sfdmu/test/`

**Convention:** Never commit anything under `datasets/sfdmu/test/`. Never add a shipped plan there. For real plans, use `datasets/sfdmu/qb/`, `mfg/`, `q3/`, `procedure-plans/`, or `scratch_data/`.

## Validation Tool

```bash
python scripts/validate_sfdmu_v5_datasets.py                           # validate all shipped plans (skips test/ and *.bak)
python scripts/validate_sfdmu_v5_datasets.py --dataset datasets/sfdmu/qb/en-US/qb-pricing  # one plan
python scripts/validate_sfdmu_v5_datasets.py --fix-all --dry-run       # preview fixes
python scripts/validate_sfdmu_v5_datasets.py --fix-all                 # apply fixes
```

The validator checks the **plan** (export.json/CSV v5 compliance). To check that the
plan's **README** still matches the plan after you edit objects/CSVs (record counts,
operations, externalIds, phantom/missing objects), run the consistency checker — it
fails (exit 1) on drift, so it doubles as a pre-merge gate. Use `--strict` (what
`pr_gate.py` actually runs) — without it, operation/externalId mismatches and
missing-object rows are WARN-level and exit 0:

```bash
python scripts/ai/check_plan_readme_consistency.py --strict                                  # all plans
python scripts/ai/check_plan_readme_consistency.py --strict datasets/sfdmu/qb/en-US/qb-pricing  # one plan
```

## Additional References

- Plan dependency graph: [plan-dependency-graph.md](plan-dependency-graph.md)
- Object-to-plan mapping: [object-plan-mapping.md](object-plan-mapping.md)
- Full v5 migration notes: `docs/references/sfdmu-composite-key-optimizations.md`
- Plan-specific guides (detailed object notes, idempotency, 260 changes):
  - `datasets/sfdmu/qb/en-US/qb-dro/README.md` — DRO plan
  - `datasets/sfdmu/qb/en-US/qb-pcm/README.md` — PCM plan
