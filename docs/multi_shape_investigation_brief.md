# Work Continuation Brief — Multi-Shape Rating Architecture Investigation

**Repo**: `bgaldino/rlm-base-dev`
**Branch**: `260-dev`
**Date**: 2026-03-01
**Status**: Investigation defined; no implementation started

---

## What Was Accomplished This Session

### 1. qb-rating / qb-rates Plans — Fully Validated and Committed

The `qb-rating` and `qb-rates` SFDMU data plans are working correctly on the `260-dev` branch. The following was completed and committed (`6cb1035`):

- `test_qb_rating_idempotency` — switched to `use_extraction_roundtrip: true`. The test performs a full roundtrip: load from source CSVs → extract from org → post-process extraction → re-import from processed dir → compare counts. Verified passing: PUR=20, PURP=17, PUG=17.
- `test_qb_rates_idempotency` — remains `use_extraction_roundtrip: false`. SFDMU v5 cannot extract 2-hop traversal fields used as components of RABT's composite key (`RateCardEntry.RateCard.Name` etc.) — extraction produces `#N/A`, breaking re-import FK resolution. Load-twice test passes: PBRC=2, RCE=19, RABT=21.
- `qb-rating/README.md` — updated idempotency section (extraction roundtrip, Active record deletion conflict, prerequisite cleanup commands, qb-rates limitation note).
- `qb-rating/README.md` — added Known Limitations / Future Work section documenting the multi-shape problem.

### 2. Critical Runtime Finding — Active Record Deletion Conflict

`deleteOldData: true` sends a direct REST DELETE. Salesforce **rejects deletion of Active PURs and PUGs** — the entire batch fails; Active records remain while new Draft records are inserted on top (count doubles). This happens when `prepare_rating` activates records before an idempotency test runs.

**Required cleanup sequence before any idempotency test**:
```bash
cci task run delete_qb_rates_data   # deactivates + deletes rates (FK to PURs)
cci task run delete_qb_rating_data  # deactivates PUG/PUR then deletes all
```

### 3. Multi-Shape Architecture Analysis — Document Written, No Implementation

The investigation revealed that the current `Insert + deleteOldData` (no WHERE) pattern is **shape-exclusive**: any re-run of one shape's plan destroys all other shapes' records. A full architecture analysis was written and is the primary output to continue.

---

## Current State of Files

### Key Committed Files (`260-dev`, commit `6cb1035`)
```
cumulusci.yml                                          — idempotency task updates
datasets/sfdmu/qb/en-US/qb-rating/export.json         — qb-rating SFDMU plan (working)
datasets/sfdmu/qb/en-US/qb-rating/ProductUsageGrant.csv
datasets/sfdmu/qb/en-US/qb-rating/ProductUsageResourcePolicy.csv
datasets/sfdmu/qb/en-US/qb-rating/README.md           — updated with multi-shape TODO
datasets/sfdmu/qb/en-US/qb-rates/export.json          — qb-rates SFDMU plan (working)
scripts/apex/activateRatingRecords.apex
scripts/apex/deleteQbRatesData.apex
tasks/rlm_sfdmu.py                                     — TestSFDMUIdempotency with roundtrip support
```

### Uncommitted New Files (staged for next commit)
```
docs/multi_shape_rating_architecture.md    — full architecture analysis (PRIMARY OUTPUT)
docs/multi_shape_investigation_brief.md   — this file
```

### Key CCI Tasks
| Task | Description |
|------|-------------|
| `insert_qb_rating_data` | Loads qb-rating plan from source CSVs |
| `insert_qb_rates_data` | Loads qb-rates plan from source CSVs |
| `delete_qb_rating_data` | Apex: deactivates → deletes PUG → PURP → PUR |
| `delete_qb_rates_data` | Apex: deletes rates data (must run before delete_qb_rating_data) |
| `activate_rating_records` | Apex: 7-step PUR/PUG activation |
| `prepare_rating` | Flow: insert_qb_rating_data + insert_qb_rates_data + activate both |
| `test_qb_rating_idempotency` | Extraction roundtrip test (requires Draft-only org state) |
| `test_qb_rates_idempotency` | Load-twice idempotency test |

### CCI Org Aliases
- Beta org CCI alias: `beta` (use `--org beta`)
- Beta org SFDX alias: `rlm-base__beta` (SFDX only, NOT for CCI commands)

---

## The Multi-Shape Problem (Summary)

### Root Cause
`Insert + deleteOldData: true` (no WHERE) owns ALL records of each type globally. Loading a second data shape wipes the first on every re-run. One shape per org is the current hard limit.

### Requirements
1. Multiple shapes coexist on the same org, independently loadable/re-runnable
2. Drift capture per shape (extract modifications, diff against baseline CSVs)
3. Test and approval workflow (diff → review → merge into base OR configure as downstream overlay)
4. CCI overlay pattern: downstream projects add their shape plans without conflicting with base

### Why Upsert Is Required
Shape isolation requires that a shape's plan run does not delete or modify sibling shapes' records. Only Upsert achieves this. `deleteOldData` cannot be scoped without a WHERE clause.

### Confirmed Constraints
1. **No custom fields** on PUR (`ProductUsageResource`), PURP (`ProductUsageResourcePolicy`), or PUG (`ProductUsageGrant`) — platform does not permit it on these API 260 SObjects.
2. **No static WHERE clauses** — any scope must be derived dynamically from the plan's own CSV contents at runtime.

### SFDMU v5 Bugs Blocking Native Upsert
| Bug | Description | Objects Affected |
|-----|-------------|-----------------|
| Bug 2 | Upsert TARGET SELECT strips prefix from 2-hop traversal columns → invalid SOQL | PURP, PUG |
| Bug 3 | Upsert with traversal externalId components never matches existing records → always inserts duplicates | PUR, PUG |

Custom fields would have bypassed both bugs (direct-field externalId), but that path is closed.

---

## The Two Options Under Investigation

### Option A — Dynamic WHERE + Insert + deleteOldData
Keep SFDMU's Insert + deleteOldData but inject a WHERE clause derived from the plan's CSV at runtime. The `LoadSFDMUData` wrapper (`tasks/rlm_sfdmu.py`) already modifies a working copy of `export.json` before running SFDMU — the same mechanism extends to WHERE injection.

```
Runtime: scan PUR CSV → extract Product SKU set → inject into export.json working copy:
  PUR:  WHERE Product.StockKeepingUnit IN ('QB-DB', 'QB-CMT-TKN-EACH', ...)
  PURP: WHERE ProductUsageResource.Product.StockKeepingUnit IN (...)   ← 2-hop, needs verification
  PUG:  WHERE UsageDefinitionProduct.StockKeepingUnit IN (...)
```

**Blocked by**: Whether Salesforce resolves a 2-hop traversal WHERE on PURP (Investigation 1) and whether SFDMU's deleteOldData actually respects WHERE (Investigation 2).
**Limitation**: Still wipe-and-reload per shape; shapes must have disjoint product sets.

### Option B — Pre-ID Resolution → True Upsert
A new pre-resolution CCI task queries the org for existing records by traversal fields, builds a natural-key → Salesforce ID map, and merges IDs into working CSV copies. SFDMU then runs with `externalId: Id` (a direct field — no traversal bugs). Records with IDs are updated; records without IDs are inserted. No `deleteOldData`.

```
Pre-resolution task:
  SELECT Id, Product.StockKeepingUnit, UsageResource.Code FROM ProductUsageResource
  → build map: "QB-DB:UR-CPUTIME" → "a0x000..."
  → merge Ids into working CSV copy

SFDMU pass 1 (Update): rows with Id populated
SFDMU pass 2 (Insert): rows without Id (net-new)
```

**Advantages over Option A**: True Upsert (no wipe-and-reload), Active record conflict eliminated, shapes can share Product2 records, per-record precision.
**Trade-off**: Higher implementation complexity (new Python task + two-pass SFDMU orchestration).

---

## Investigation Plan (The Next Step)

Six investigations defined in `docs/multi_shape_rating_architecture.md`. Run in this order:

| # | Investigation | Method | Gates |
|---|--------------|--------|-------|
| 1 | SOQL: does 2-hop traversal WHERE resolve on PURP? | `sf data query "SELECT Id FROM ProductUsageResourcePolicy WHERE ProductUsageResource.Product.StockKeepingUnit IN ('QB-DB')"` | Go/no-go for Option A |
| 2 | SFDMU: does `deleteOldData` respect WHERE clause? | Run WHERE-scoped plan on sandbox; verify only matching records deleted | Go/no-go for Option A |
| 3 | Dynamic WHERE injection in `LoadSFDMUData` | Prototype in `tasks/rlm_sfdmu.py`; test edge cases (empty set, large set >1000) | Implementation task if 1+2 pass |
| 4 | Pre-ID resolution queries feasible? | Run the three SELECT queries (PUR, PURP, PUG) against a populated org; verify natural keys are unique and match CSV keys | Go/no-go for Option B |
| 5 | SFDMU Upsert with `externalId: Id` | Test with mixed CSV (some rows with Id, some without); verify Update/Insert routing | Implementation task if 4 passes |
| 6 | End-to-end multi-shape coexistence | Load Shape A, load Shape B, re-run Shape A, verify Shape B untouched | Required for either option |

**Quick start**: Investigations 1 and 4 can be run immediately on any org with rating data loaded. They are read-only (SELECT queries only) and take minutes.

---

## Files to Read First on a New Session

1. **`docs/multi_shape_rating_architecture.md`** — full architecture analysis with detailed option descriptions, investigation procedures, and decision matrix
2. **`datasets/sfdmu/qb/en-US/qb-rating/README.md`** — plan documentation including Known Limitations / Future Work section
3. **`tasks/rlm_sfdmu.py`** — `LoadSFDMUData`, `ExtractSFDMUData`, `TestSFDMUIdempotency` classes; the wrapper mechanism for WHERE injection lives here
4. **`datasets/sfdmu/qb/en-US/qb-rating/export.json`** — current SFDMU plan; the starting point for any multi-shape plan variant

---

## What Has NOT Been Started

- No implementation of dynamic WHERE injection
- No pre-ID-resolution task written
- No multi-shape plan variants created
- No refactoring of Apex cleanup scripts to be shape-scoped
- Investigations 1–6 have not been run
