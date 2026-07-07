# qb-clm Data Plan

SFDMU data plan for QuantumBit (QB) Contract Lifecycle Management (CLM)
configuration: clause category configuration, document clause sets, and the
Object State Management (OSM) definitions that drive contract lifecycle
transitions (states, actions, and transition rules).

## CCI Integration

### Flow: `prepare_clm`

This plan is executed as **step 1** of the `prepare_clm` flow (when
`clm=true` and `clm_data=true`).

| Step | Task              | When              | Description          |
|------|-------------------|--------------------|-----------------------|
| 1    | `insert_clm_data` | clm + clm_data     | Runs this SFDMU plan |

### Task Definitions

```yaml
insert_clm_data:
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-clm"
```

`insert_clm_data_prod` (same `class_path`/`pathtoexportjson`) is also
registered for production targets. Also wired: `extract_qb_clm_data`
(`ExtractSFDMUData`) and `test_qb_clm_idempotency` (`TestSFDMUIdempotency`,
no extraction roundtrip).

## Data Plan Overview

Single-pass plan, 7 objects, ordered parent → child:

| # | Object                          | Operation | External ID                        | Records |
|---|----------------------------------|-----------|-------------------------------------|---------|
| 1 | ClauseCatgConfiguration          | Upsert    | `DeveloperName`                     | 2       |
| 2 | DocumentClauseSet                 | Upsert    | `Name;CategoryReference.DeveloperName` | 20  |
| 3 | ObjectStateDefinition             | Upsert    | `Name`                               | 2       |
| 4 | ObjectStateActionDefinition       | Upsert    | `Name`                               | 11      |
| 5 | ObjectStateValue                  | Upsert    | `Name`                               | 24      |
| 6 | ObjectStateTransition              | Upsert    | `Name`                               | 47      |
| 7 | ObjectStateTransitionAction        | Upsert    | `Name`                               | 41      |

## externalId / $$ Notes

- `DocumentClauseSet` is the only object with a `$$` composite key column
  (`$$Name$CategoryReference.DeveloperName`), matching its composite
  `externalId: Name;CategoryReference.DeveloperName`.
- All other objects use a single direct-field `externalId` (`Name` or
  `DeveloperName`) with plain-field CSV headers — no `$$` column needed.
- `ObjectStateTransition.csv` carries a `CustomPermission.DeveloperName`
  traversal column for an optional lookup, but `CustomPermission` itself is
  not loaded by this plan (see below).

## Unreferenced / Not-Loaded CSVs

Two CSVs sit in this plan's directory but are **not referenced by
`export.json`** and are not loaded:

- **`CustomPermission.csv`** — empty (0 bytes, no header). `CustomPermission`
  is a metadata-managed object; this file is a placeholder/leftover and
  loads nothing.
- **`OmniProcess.csv`** — 1 record (`SalesforceContractsCustomAction`),
  reference-only. `OmniProcess` records here are managed-package/metadata
  artifacts, not created by this plan.

Neither file should be treated as part of the plan's data contract; if CLM
grows to need either object, add it to `export.json` explicitly.

## File Structure

```
qb-clm/
├── export.json                          # SFDMU data plan (1 pass, 7 objects)
├── README.md                             # This file
├── ClauseCatgConfiguration.csv           # 2 records
├── DocumentClauseSet.csv                 # 20 records
├── ObjectStateDefinition.csv             # 2 records
├── ObjectStateActionDefinition.csv       # 11 records
├── ObjectStateValue.csv                  # 24 records
├── ObjectStateTransition.csv             # 47 records
├── ObjectStateTransitionAction.csv       # 41 records
├── CustomPermission.csv                  # 0 records (empty — not in export.json, not loaded)
└── OmniProcess.csv                       # 1 record (not in export.json, not loaded — reference only)
```
