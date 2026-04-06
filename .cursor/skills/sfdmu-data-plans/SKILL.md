---
name: sfdmu-data-plans
description: >-
  SFDMU v5 data plan authoring and review for Revenue Cloud. Use when creating,
  modifying, or reviewing export.json files, CSV data files, or SFDMU data plans.
  Covers v5 rules, known bugs, externalId patterns, operation selection,
  deleteOldData safety, and cross-plan dependencies.
---

# SFDMU v5 Data Plans

SFDMU v5.0.0+ is required. v4 syntax is not supported.

## Quick Rules

1. externalId delimiter is `;` — NOT `$$` (that's v4).
2. Relationship-traversal in externalId → use `Insert` + `deleteOldData: true`.
3. Never change Upsert → Insert+deleteOldData without explicit user approval.
4. Empty CSV → set `excluded: true` (prevents destructive wipe).
5. Parent → child order in `objects` array (deletion runs reverse).
6. `$$` CSV column must match externalId fields exactly.
7. After extraction: run `post_process_extraction.py` to add `$$` columns.

## DO NOT

- **DO NOT** use `$$Field1$Field2` syntax in `externalId` (v4, not v5)
- **DO NOT** change `Upsert` to `Insert+deleteOldData` without user approval
- **DO NOT** leave empty CSVs without `excluded: true`
- **DO NOT** use `$$` composite notation for lookup reference columns in CSVs (Bug 4 — self-referential and cross-object `$$` references fail on import; use simple field references)
- **DO NOT** rely on composite `externalId` with all-traversal fields (e.g. `Parent.Name;OtherParent.Name`) for upsert matching (Bug 5 — SFDMU cannot resolve composite keys composed entirely of relationship traversals; use `deleteOldData: true` instead)

## export.json Structure

```json
{
  "apiVersion": "66.0",
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
| externalId uses any relationship traversal | `Insert` | `true` | Bug 3: Upsert never matches on traversals |
| Auto-number Name + all-relationship externalId | `Insert` | `true` | Bug 1 + Bug 3 |
| Read-only reference (already loaded by another plan) | `Readonly` | `false` | Just resolves IDs for child lookups |
| Updating existing records (set fields) | `Update` | `false` | Only modifies matched records |
| Empty CSV (no records yet) | mark `excluded: true` | — | Prevents destructive delete-on-load |

## Bug 4 — `$$` Composite Key Self-References Fail on Import

**Problem:** When an object has a self-referential lookup (e.g., `ProductComponentGroup.ParentGroupId` → `ProductComponentGroup`) and the CSV uses `$$` composite key notation for that reference (e.g., `ParentGroup.$$Code$ParentProduct.StockKeepingUnit`), SFDMU cannot resolve the parent record. The MissingParentRecordsReport shows anonymized hashes instead of matched records, and the lookup fields are left null after import — even though the parent records exist and SFDMU runs multiple passes.

**Root cause:** SFDMU's `$$` composite notation works for the *primary* record's externalId matching (source↔target), but fails when used as a *lookup reference column* for self-referential relationships. SFDMU cannot decompose a composite `$$` value back into individual fields to find the referenced parent record.

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

**Audit required:** All data plans with `$$` composite columns used as *lookup references* (not just primary keys) should be reviewed. Cross-object `$$` references (e.g., `ProductComponentGroup.$$Code$...` referenced from `ProductRelatedComponent`) may also be affected — test each case.

## The Three v5 Bugs

**Bug 1 — All-multi-hop externalId fails validation**
When externalId contains ONLY relationship-traversal components (2+ hops), SFDMU raises `{Object} has no mandatory external Id field definition`.
Fix: Include at least one direct field in externalId.

**Bug 2 — 2-hop traversal columns cause SOQL injection**
SFDMU strips the first-hop prefix from 2-hop CSV columns in the Upsert TARGET SELECT, producing invalid SOQL.
Fix: Use `Insert` + `deleteOldData: true` (Insert skips TARGET SELECT).

**Bug 3 — Upsert with relationship-traversal externalId never matches**
Even 1-hop relationship traversals (e.g. `Product.StockKeepingUnit;UsageResource.Code`) cause Upsert to always insert, creating duplicates.
Fix: Use `Insert` + `deleteOldData: true`.

## CRITICAL — Insert + deleteOldData Safety

**Never change Upsert to Insert + deleteOldData without:**
1. Explaining which Bug (2 or 3) makes Upsert impossible
2. Confirming no direct-field externalId alternative exists
3. Getting explicit user approval

`deleteOldData: true` deletes ALL existing records before inserting. Misapplied, it wipes data that Upsert would have safely matched.

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

## Multi-Pass Architecture

Some plans use multiple objectSets (passes) to handle circular dependencies or activation ordering:
- **Pass 1**: Insert records in Draft/Inactive status
- **Pass 2**: Update records to Active status (after dependencies exist)
- **Pass 3**: Set cross-references that require both ends to exist

Example: `qb-billing` uses 3 passes: draft insert → activate treatment items → activate treatments and set BillingPolicy.DefaultBillingTreatmentId.

## Review Checklist

- [ ] externalId uses `;` delimiters (not `$$`)
- [ ] No relationship-traversal externalId with `operation: Upsert` (use Insert + deleteOldData)
- [ ] ORDER BY fields present in SELECT clause
- [ ] Relationship traversal columns in SOQL match CSV headers
- [ ] Empty CSVs have `excluded: true`
- [ ] Objects ordered parent → child
- [ ] `$$` composite key CSV headers match externalId fields exactly
- [ ] deleteOldData only used where justified (Bug 2/3)
- [ ] No `$$` composite notation used for lookup reference columns (Bug 4 — use simple field references instead)
- [ ] Self-referential lookups use simple field references (e.g., `ParentGroup.Code` not `ParentGroup.$$Code$...`)

## Validation Tool

```bash
python scripts/validate_sfdmu_v5_datasets.py                           # validate all
python scripts/validate_sfdmu_v5_datasets.py --dataset datasets/sfdmu/qb/en-US/qb-pricing  # one plan
python scripts/validate_sfdmu_v5_datasets.py --fix-all --dry-run       # preview fixes
python scripts/validate_sfdmu_v5_datasets.py --fix-all                 # apply fixes
```

## Additional References

- Plan dependency graph: [plan-dependency-graph.md](plan-dependency-graph.md)
- Object-to-plan mapping: [object-plan-mapping.md](object-plan-mapping.md)
- Full v5 migration notes: `docs/references/sfdmu-composite-key-optimizations.md`
- Plan-specific guides (detailed object notes, idempotency, 260 changes):
  - `datasets/sfdmu/qb/en-US/qb-dro/README.md` — DRO plan
  - `datasets/sfdmu/qb/en-US/qb-pcm/README.md` — PCM plan
