# qb-transactionprocessingtypes Data Plan

SFDMU data plan for QuantumBit (QB) Transaction Processing Types. Creates the `TransactionProcessingType` metadata records required for the Standard Configurator, Advanced Configurator, and Advanced Config with Fetch Rates engines. These records must exist before constraint metadata can be deployed.

Salesforce documentation: [TransactionProcessingType (Tooling API)](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/tooling_api_objects_transactionprocessingtype.htm)

## CCI Integration

### Flow: `prepare_constraints`

This plan is executed as **step 1** of the `prepare_constraints` flow (when `constraints=true`, `qb=true`).

| Step | Task                                        | Description                                          |
|------|---------------------------------------------|------------------------------------------------------|
| 1    | `insert_qb_transactionprocessingtypes_data` | Runs this SFDMU plan (single pass, Upsert)           |
| 2    | `deploy_post_constraints`                   | Deploys constraint metadata                          |
| 3    | `assign_permission_sets`                    | Assigns constraint permission sets (TSO + ProcPlans) |
| 4    | `apply_context_constraint_engine_node_status` | Applies constraint engine node status              |

### Task Definition

```yaml
insert_qb_transactionprocessingtypes_data:
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes"
```

## Data Plan Overview

The plan uses a **single SFDMU pass** with one Upsert object. `excludeIdsFromCSVFiles: "true"` for cross-org portability.

```text
Single Pass (SFDMU)
───────────────────────────────────
Upsert TransactionProcessingType
(3 records: Standard + Advanced + AdvFetchConfig)
```

### Objects

| # | Object                    | Operation | External ID     | Records |
|---|---------------------------|-----------|-----------------|---------|
| 1 | TransactionProcessingType | Upsert    | `DeveloperName` | 3       |

### Records

| DeveloperName        | MasterLabel            | RuleEngine           | SaveType | PricingPreference | RatingPreference | TaxPreference |
|----------------------|------------------------|----------------------|----------|-------------------|------------------|---------------|
| AdvFetchConfig       | Adv Config Fetch Rates | AdvancedConfigurator | Standard | System            | Fetch            |               |
| StandardConfigurator | Standard Configurator  | StandardConfigurator | Standard |                   |                  |               |
| AdvancedConfigurator | Advanced Configurator  | AdvancedConfigurator | Standard |                   |                  |               |

## Portability

- **External ID**: `DeveloperName` — fully portable across orgs ("AdvFetchConfig", "StandardConfigurator", "AdvancedConfigurator")
- **No auto-numbered fields**
- **No composite keys or `$$` columns**

## Dependencies

**Upstream:**

- None — TransactionProcessingType has no parent object dependencies

**Downstream:**

- **Constraint metadata deployment** (`deploy_post_constraints`) depends on these records existing
- The configurator engine references these records at runtime

## File Structure

```text
qb-transactionprocessingtypes/
├── export.json                                # SFDMU data plan (single pass, 1 object)
├── README.md                                  # This file
├── TransactionProcessingType.csv              # 3 records (Upsert)
│
│  SFDMU Runtime (gitignored)
├── source/                                    # SFDMU-generated source snapshots
└── target/                                    # SFDMU-generated target snapshots
```

## Idempotency

Uses `Upsert` with `DeveloperName` as the external ID — when `DeveloperName` is unique per record in the org, re-runs match existing records and update in place, so no additional duplicates are created by this plan. Pre-existing duplicates (if any) are preserved.

## Schema Analysis

### Creatable/Updatable Fields

| Field               | Type     | Creatable | Updatable | Nillable | Unique | IdLookup | In SOQL? |
|---------------------|----------|-----------|-----------|----------|--------|----------|----------|
| `Description`       | string   | Yes       | Yes       | Yes      | No     | No       | Yes      |
| `DeveloperName`     | string   | Yes       | Yes       | No       | No     | No       | Yes      |
| `Language`          | picklist | Yes       | Yes       | Yes      | No     | No       | Yes      |
| `MasterLabel`       | string   | Yes       | Yes       | No       | No     | No       | Yes      |
| `PricingPreference` | picklist | Yes       | Yes       | Yes      | No     | No       | Yes      |
| `RatingPreference`  | picklist | Yes       | Yes       | Yes      | No     | No       | Yes      |
| `RuleEngine`        | picklist | Yes       | Yes       | Yes      | No     | No       | Yes      |
| `SaveType`          | picklist | Yes       | Yes       | No       | No     | No       | Yes      |
| `TaxPreference`     | picklist | Yes       | Yes       | Yes      | No     | No       | Yes      |

### Read-Only / System Fields (not in SOQL)

| Field              | Type      |
|--------------------|-----------|
| `Id`               | id        |
| `CreatedById`      | reference |
| `CreatedDate`      | datetime  |
| `LastModifiedById` | reference |
| `LastModifiedDate` | datetime  |
| `SystemModstamp`   | datetime  |
| `IsDeleted`        | boolean   |
| `ManageableState`  | picklist  |
| `NamespacePrefix`  | string    |

### Field Descriptions and Valid Values

**`Description`** (string, nillable) — Free-text description to help admins with configuration.

**`DeveloperName`** (string, required) — API name (expected unique per org by convention). Alphanumeric and underscores only; must begin with a letter, no spaces, no trailing or consecutive underscores.

**`Language`** (picklist, restricted, nillable) — Language of the record. Valid values: `da` (Danish), `de` (German), `en_US` (English), `es` (Spanish), `es_MX` (Spanish Mexico), `fi` (Finnish), `fr` (French), `it` (Italian), `ja` (Japanese), `ko` (Korean), `nl_NL` (Dutch), `no` (Norwegian), `pt_BR` (Portuguese Brazil), `ru` (Russian), `sv` (Swedish), `th` (Thai), `zh_CN` (Chinese Simplified), `zh_TW` (Chinese Traditional).

**`MasterLabel`** (string, required) — Display label for the record.

**`PricingPreference`** (picklist, restricted, nillable) — Controls price calculation per sales transaction. Available in API v65.0+. Valid values:

- `Force` — Reprices all lines.
- `System` — Delta pricing on unprocessed lines (when Delta Pricing is enabled).
- `Skip` — Skips pricing on all lines.

**`RatingPreference`** (picklist, nillable) — Controls whether catalog rates are fetched during quote creation. Available in API v66.0+ (requires Rate Management enabled). Valid value:

- `Fetch` — Retrieves and saves catalog rates for usage resources. If not specified, catalog rates are not saved by default.

**`RuleEngine`** (picklist, restricted, nillable) — Rule engine for processing rules. Valid values:

- `AdvancedConfigurator`
- `StandardConfigurator`

**`SaveType`** (picklist, restricted, required) — How transaction results are processed on save. Valid values:

- `Standard`
- `Large` — Reserved for future use.

**`TaxPreference`** (picklist, restricted, nillable) — Controls tax calculation per sales transaction. Available in API v65.0+. Valid value:

- `Skip` — Skips tax calculation. If not specified, tax calculation runs by default.

### Key Findings

- **No polymorphic fields, no self-referencing fields, no lookup references** — standalone metadata-like object.
- **`DeveloperName`** — not schema-unique (`IsUnique=false`, `IsIdLookup=false`). Used as `externalId` by convention (standard pattern for CMDT-like records). Platform may enforce uniqueness via application logic.
- **No schema-enforced unique fields** — SFDMU relies on data-level uniqueness for `DeveloperName`. Uses `Upsert` with `DeveloperName` as externalId to ensure idempotency.
- **Single-field key** (`DeveloperName`) — no composite keys needed.

## Optimization Opportunities

1. **Extraction available**: Use `extract_qb_transactionprocessingtypes_data` (Data Management - Extract). Run all extracts: `cci flow run run_qb_extracts --org <org>`. Idempotency: `test_qb_transactionprocessingtypes_idempotency` / `cci flow run run_qb_idempotency_tests --org <org>`.
