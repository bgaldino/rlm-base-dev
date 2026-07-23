# Delta Term Builder — Geography reference data

Seed data for the **`DL_Geography__c`** master/reference object
(`unpackaged/post_term_builder/objects/DL_Geography__c/`). It stands up a small,
self-contained geography hierarchy — airports → cities → countries → regions →
super-regions — that Delta contracting analysts use as the normalized reference
table behind term scoping (single airport, city grouping, country, entity/region,
super-region).

This object is **standalone master data**: it is independent of the Term Builder
LWC engine today, but its `DL_Geography_Type__c` taxonomy (Airport → Super-region,
plus Custom Group) and its codes align with the route endpoint picklist strings
(`ATL`, `LHR`, `JFK`, `US50`, `EMEAI`) so it can be wired into term-scope resolution
later.

## Hierarchy model

Each row carries a canonical `DL_Code__c` (external id) and an optional self-lookup
`DL_Parent_Geography__c` to the next-broader geography. Two trees are seeded:

```
EMEAI (Super-region)
└─ EUROPE (Region)
   └─ GB (Country)
      └─ LON (City)
         └─ LHR (Airport)

NORTHAM (Super-region)
└─ US50 (Region)
   └─ USA (Country)
      ├─ NYC (City)      └─ JFK (Airport)
      └─ ATL-CITY (City) └─ ATL (Airport)
```

The self-lookup gives each geography exactly one parent. Overlapping **Custom
Group** scopes (e.g. a joint-venture route set that crosses the normal hierarchy)
are a deferred many-to-many concern and are not seeded here.

## Load order & operations

Single object, **Upsert** on the direct field `DL_Code__c` (satisfies SFDMU v5
Bug 1 — the external id is a real field, not an all-traversal composite). The
self-referential parent is resolved with a **single-field** reference
`DL_Parent_Geography__r.DL_Code__c` (satisfies Bug 4 — never a `$$` composite for a
self lookup). Rows are ordered parent-before-child in the CSV so parents resolve on
a first run against an empty org.

| # | Object | Operation | External ID | Records |
|---|--------|-----------|-------------|---------|
| 1 | DL_Geography__c | Upsert | `DL_Code__c` | 12 |

The direct-field Upsert makes the plan idempotent — rerunning matches existing
`DL_Geography__c` records by code rather than duplicating them. No `deleteOldData`;
targets a clean demo org.

## Files

```
export.json           # 1-object plan (this dir)
DL_Geography__c.csv   # 12 records  (2 super-regions, 2 regions, 2 countries, 3 cities, 3 airports)
```

## Prerequisite — FLS

`DL_Geography__c` and its fields are deployed with the `post_term_builder` bundle.
**Assign `RLM_TermBuilderPermset` to the loading user before running this plan** —
SFDMU silently drops fields the running user cannot edit, so without FLS the
geography rows would load with blank `DL_Code__c` / type / parent.

## Run

Ad-hoc load (no CCI task — this is reference data loaded on demand):

```bash
sf sfdmu run --sourceusername csvfile --targetusername Delta \
  --path datasets/sfdmu/dl/en-US/dl-geographies
```

Verify:

```bash
sf data query \
  -q "SELECT DL_Code__c, DL_Geography_Type__c, DL_Parent_Geography__r.DL_Code__c FROM DL_Geography__c ORDER BY DL_Geography_Type__c" \
  --target-org Delta
```

## Validation

```bash
python scripts/validate_sfdmu_v5_datasets.py --dataset datasets/sfdmu/dl/en-US/dl-geographies
python scripts/ai/check_plan_readme_consistency.py datasets/sfdmu/dl/en-US/dl-geographies
```
