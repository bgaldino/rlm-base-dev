# qb-transactionprocessingtypes Data Plan

SFDMU data plan for QuantumBit (QB) Transaction Processing Types. Creates the `TransactionProcessingType` metadata records required for the Standard and Advanced Configurator engines. These records must exist before constraint metadata can be deployed.

## CCI Integration

### Flow: `prepare_constraints`

This plan is executed as **step 1** of the `prepare_constraints` flow (when `constraints=true`, `qb=true`).

| Step | Task                                        | Description                                            |
|------|---------------------------------------------|--------------------------------------------------------|
| 1    | `insert_qb_transactionprocessingtypes_data` | Runs this SFDMU plan (single pass, Insert)             |
| 2    | `deploy_post_constraints`                   | Deploys constraint metadata                            |
| 3    | `assign_permission_sets`                    | Assigns constraint permission sets (TSO + ProcPlans)   |
| 4    | `apply_context_constraint_engine_node_status` | Applies constraint engine node status               |

### Task Definition

```yaml
insert_qb_transactionprocessingtypes_data:
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes"
```

## Data Plan Overview

The plan uses a **single SFDMU pass** with one Insert-only object.

```
Single Pass (SFDMU)
───────────────────────────────────
Insert TransactionProcessingType
(2 records: Standard + Advanced)
```

### Objects

| # | Object                      | Operation | External ID     | Records |
|---|-----------------------------|-----------|-----------------|---------|
| 1 | TransactionProcessingType   | Insert    | `DeveloperName` | 2       |

### Records

| DeveloperName          | MasterLabel              | RuleEngine              | SaveType |
|------------------------|--------------------------|-------------------------|----------|
| StandardConfigurator   | Standard Configurator    | StandardConfigurator    | Standard |
| AdvancedConfigurator   | Advanced Configurator    | AdvancedConfigurator    | Standard |

## Configuration

### Notable Settings

- **`operation: "Insert"`** — Uses Insert, not Upsert. This means:
  - Re-runs will attempt to insert duplicates (unless SFDMU detects existing records by `DeveloperName`)
  - The `externalId: "DeveloperName"` is specified but only used for CSV-to-record matching, not for upsert deduplication
- **`excludeIdsFromCSVFiles: "false"`** — Raw Salesforce IDs may be present in CSV files (portability concern)

## Portability

- **External ID**: `DeveloperName` — fully portable across orgs ("StandardConfigurator", "AdvancedConfigurator")
- **No auto-numbered fields**
- **No composite keys or `$$` columns**

### PORTABILITY CONCERN: `excludeIdsFromCSVFiles: "false"`

Like qb-tax, this plan sets `excludeIdsFromCSVFiles: "false"`. The `source/` directory CSV contains raw Salesforce IDs. While the root `TransactionProcessingType.csv` does not include Id columns, the source/target files do.

**Recommended fix:** Change to `excludeIdsFromCSVFiles: "true"` for consistency with other plans.

## Idempotency

### IDEMPOTENCY CONCERN: `Insert` Operation

This plan uses `operation: "Insert"` instead of `"Upsert"`. This means:
- On first run: 2 records are created successfully
- On re-run: SFDMU may attempt to insert duplicates, which could fail if `DeveloperName` has a unique constraint, or succeed and create duplicate records

**Recommended fix:** Change `operation` from `"Insert"` to `"Upsert"` so that re-runs match existing records by `DeveloperName` and skip them. This would make the plan idempotent.

**Not yet validated** — idempotency testing against a 260 org is pending.

## Dependencies

**Upstream:**
- None — TransactionProcessingType has no parent object dependencies

**Downstream:**
- **Constraint metadata deployment** (`deploy_post_constraints`) depends on these records existing
- The configurator engine references these records at runtime

## File Structure

```
qb-transactionprocessingtypes/
├── export.json                                # SFDMU data plan (single pass, 1 object)
├── README.md                                  # This file
├── TransactionProcessingType.csv              # 2 records (Insert)
│
│  SFDMU Runtime (gitignored)
├── source/                                    # SFDMU-generated source snapshots
└── target/                                    # SFDMU-generated target snapshots
```

## 260 Schema Analysis (Confirmed via Org Describe)

Schema was queried against a 260 scratch org. Findings below.

### Polymorphic Fields

**None found.**

### Self-Referencing Fields

**None found.**

### Schema Changes

**`RuleEngine` field — NOT in 260 schema!**

The current SOQL query includes `RuleEngine`:
```sql
SELECT Description, DeveloperName, Language, MasterLabel, RuleEngine, SaveType FROM TransactionProcessingType
```

However, the 260 schema describe does **not** return a `RuleEngine` field. The complete list of non-system fields is:

| Field               | Type     | Updateable | In Current SOQL? |
|---------------------|----------|------------|-------------------|
| `DeveloperName`     | STRING   | Yes        | Yes               |
| `Language`          | PICKLIST | Yes        | Yes               |
| `MasterLabel`       | STRING   | Yes        | Yes               |
| `NamespacePrefix`   | STRING   | No         | Yes (read-only)   |
| `SaveType`          | PICKLIST | Yes        | Yes               |
| `Description`       | STRING   | Yes        | Yes               |
| `PricingPreference` | PICKLIST | Yes        | **No — MISSING**  |
| `TaxPreference`     | PICKLIST | Yes        | **No — MISSING**  |
| `RatingPreference`  | PICKLIST | Yes        | **No — MISSING**  |

**Findings:**
1. **`RuleEngine` may have been removed or renamed in 260** — the SOQL query will fail if this field no longer exists. This needs urgent validation: run the SFDMU plan against a 260 org to confirm. If removed, the SOQL and CSV must be updated.
2. **3 new picklist fields not in SOQL** — `PricingPreference`, `TaxPreference`, `RatingPreference` control which pricing, tax, and rating engines are used by the transaction processing type. These are likely important for 260 configurator behavior.

### Impact Assessment

- **`RuleEngine` removal**: **Critical** — the SOQL query will fail if this field no longer exists. Must be validated immediately.
- **`PricingPreference`**: Controls which pricing engine is used (e.g., standard vs. custom). **High priority** for full 260 support.
- **`TaxPreference`**: Controls which tax engine is invoked. **High priority** for tax integration scenarios.
- **`RatingPreference`**: Controls which rating engine is used. **High priority** for usage-based pricing scenarios.

### Cross-Object Dependencies

No lookup references — `TransactionProcessingType` is a standalone metadata-like object.

## External ID / Composite Key Analysis (Confirmed via Org Describe)

### Schema-Enforced Unique Fields

**None found.** `DeveloperName` is **not schema-unique** (`isUnique=false`, `isIdLookup=false`). Neither is `MasterLabel`.

This means the platform does not enforce uniqueness on TransactionProcessingType DeveloperName at the schema level. However, as a metadata-like object, Salesforce may enforce uniqueness via application logic (similar to CustomMetadataType records).

### ExternalId Assessment

| Field          | isUnique | isIdLookup | isExternalId | Assessment |
|----------------|----------|------------|--------------|------------|
| `DeveloperName`| No       | No         | No           | ⚠️ Used as externalId but no schema enforcement |
| `MasterLabel`  | No       | No         | No           | Not an alternative |

The `DeveloperName` choice is correct for this object type (standard pattern for CMDT-like records), but the lack of schema-level uniqueness means SFDMU relies on data-level uniqueness. Combined with the `Insert` operation, this creates a duplicate risk.

### Composite Key Simplification

Single-field key (`DeveloperName`) — no composite keys, no simplification needed. The key is as simple as it can be.

## Optimization Opportunities

1. **Fix `RuleEngine` field**: Validate whether `RuleEngine` exists in 260 — if removed, update SOQL query and CSV to remove it
2. **Add new preference fields**: Add `PricingPreference`, `TaxPreference`, `RatingPreference` to the SOQL query and CSV
3. **Fix idempotency**: Change `operation` from `"Insert"` to `"Upsert"` using `DeveloperName` as the external ID
4. **Fix `excludeIdsFromCSVFiles`**: Change from `"false"` to `"true"` for portability
5. **Add extraction support**: Create `extract_qb_transactionprocessingtypes_data` CCI task
6. **Consistency**: Uses `objectSets` wrapper with a misleading name "First Pass - Insert/Upsert with Draft Status" (there is no second pass and no Draft status involved) — simplify to flat `objects` array and remove the misleading name
