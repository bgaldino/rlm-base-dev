# qb-tax Data Plan

SFDMU data plan for QuantumBit (QB) tax configuration. Creates legal entities, tax engine/provider records, tax policies, tax treatments, and assigns the tax policy to products. Uses a 2-pass architecture: Pass 1 inserts records in Draft status, Pass 2 activates and sets defaults.

## CCI Integration

### Flow: `prepare_tax`

This plan is executed as **step 2** of the `prepare_tax` flow (when `tax=true`, `qb=true`, `refresh=false`).

| Step | Task                     | Description                                                |
|------|--------------------------|------------------------------------------------------------|
| 1    | `create_tax_engine`      | Runs `createTaxEngine.apex` (creates TaxEngineProvider + TaxEngine via REST API) |
| 2    | `insert_tax_data`        | Runs this SFDMU plan (2 passes)                            |
| 4    | `activate_tax_records`   | Runs `activateTaxRecords.apex`                             |

### Task Definition

```yaml
insert_tax_data:
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-tax"
```

## Data Plan Overview

The plan uses **2 SFDMU passes** plus an **Apex prerequisite** and **Apex activation**:

```
Apex Prerequisite       Pass 1 (SFDMU)           Pass 2 (SFDMU)          Apex Activation
──────────────────      ─────────────────        ─────────────────       ─────────────────
createTaxEngine.apex -> Insert/Upsert all   ->   Activate TaxTreatment   activateTaxRecords.apex
(TaxEngineProvider +    objects in Draft          + set TaxPolicy          (activates remaining
 TaxEngine via REST)    + assign TaxPolicy         defaults                TaxTreatment + TaxPolicy)
                        to Product2
```

### Pass 1 — Insert/Upsert with Draft Status

| # | Object           | Operation | External ID                        | Records |
|---|------------------|-----------|------------------------------------|---------|
| 1 | LegalEntity      | Upsert    | `Name`                             | 2       |
| 2 | TaxEngineProvider| Upsert    | `DeveloperName`                    | 1       |
| 3 | TaxEngine        | Upsert    | `TaxEngineName`                    | 1       |
| 4 | TaxTreatment     | Upsert    | `Name;LegalEntity.Name;TaxPolicy.Name` | 1   |
| 5 | TaxPolicy        | Upsert    | `Name`                             | 1       |
| 6 | Product2         | Update    | `StockKeepingUnit`                 | 164     |

**Note:** TaxTreatment and TaxPolicy use `skipExistingRecords: true` to avoid updating records that already exist. Product2 is Update-only (sets `TaxPolicyId`). The `create_tax_engine` Apex script creates TaxEngineProvider and TaxEngine via REST API before this SFDMU pass runs, so the SFDMU upsert of those objects acts as a safety net.

### Pass 2 — Activate and Set Defaults

| # | Object       | Operation | External ID                        | Records |
|---|--------------|-----------|------------------------------------|---------|
| 1 | TaxTreatment | Update    | `Name;LegalEntity.Name;TaxPolicy.Name` | 1   |
| 2 | TaxPolicy    | Update    | `Name`                             | 1       |

Pass 2 activates TaxTreatment (sets `Status`) and sets `DefaultTaxTreatmentId` on TaxPolicy.

## Apex Scripts

### `createTaxEngine.apex` (Prerequisite)

Creates the TaxEngineProvider and TaxEngine via REST API callout. Requires:
- `ApexClass` named `RC_MockTaxAdapter` (deployed as metadata)
- `NamedCredential` named `RLM_MockTax` (deployed as metadata)

The script creates the TaxEngineProvider via REST API (because it cannot be inserted via standard DML), then creates a TaxEngine record linked to it.

### `activateTaxRecords.apex` (Activation)

Activates tax records in dependency order:
1. TaxTreatment: Sets all non-Active records to `Status = 'Active'`
2. TaxPolicy: Sets all non-Active records to `Status = 'Active'`

The script is idempotent — queries filter on `Status != 'Active'`.

## Configuration

### Notable Settings

- **`excludeIdsFromCSVFiles: "false"`** — Raw Salesforce IDs are included in CSVs. This is a **portability concern** as IDs are org-specific.
- **`useSeparatedCSVFiles: true`** — SFDMU uses `objectset_source/` subdirectories for pass-specific CSV overrides.
- **`skipExistingRecords: true`** on TaxTreatment and TaxPolicy — prevents overwriting existing records on re-runs.

## Portability

### PORTABILITY CONCERN: `excludeIdsFromCSVFiles: "false"`

Unlike most other QB plans, this plan sets `excludeIdsFromCSVFiles: "false"`, meaning raw Salesforce IDs may be present in the CSV files. These IDs are org-specific and will not resolve correctly in a different org.

**Recommended fix:** Change to `excludeIdsFromCSVFiles: "true"` and ensure all lookup relationships use relationship traversal fields (e.g., `TaxPolicy.Name` instead of `TaxPolicyId`).

### External IDs

All external IDs use portable fields:
- `Name` for LegalEntity, TaxPolicy (human-readable: "Default Legal Entity - US", "Default Tax Policy")
- `DeveloperName` for TaxEngineProvider
- `TaxEngineName` for TaxEngine
- `StockKeepingUnit` for Product2
- `Name;LegalEntity.Name;TaxPolicy.Name` for TaxTreatment (composite, all human-readable)

No auto-numbered Name fields are used.

## Dependencies

**Upstream:**
- **qb-pcm** — Product2 records must exist (matched by `StockKeepingUnit`)
- **Metadata deployment** — `RC_MockTaxAdapter` Apex class and `RLM_MockTax` NamedCredential must be deployed

**Downstream:**
- None directly — tax configuration is consumed at runtime by the billing/invoicing engine

## File Structure

```
qb-tax/
├── export.json                          # SFDMU data plan (2 passes, 8 objects)
├── README.md                            # This file
│
│  Source CSVs (Pass 1 - Draft status)
├── LegalEntity.csv                      # 2 records
├── TaxEngineProvider.csv                # 1 record
├── TaxEngine.csv                        # 1 record
├── TaxTreatment.csv                     # 1 record
├── TaxPolicy.csv                        # 1 record
├── Product2.csv                         # 164 records (Update only)
├── NamedCredential.csv                  # 1 record (reference only)
│
│  Source CSVs (Pass 2 - Activate)
├── objectset_source/
│   └── object-set-2/
│       ├── TaxTreatment.csv             # 1 record (Status -> Active)
│       └── TaxPolicy.csv               # 1 record (DefaultTaxTreatment + Status)
│
│  SFDMU Runtime (gitignored)
├── source/                              # SFDMU-generated source snapshots
└── target/                              # SFDMU-generated target snapshots
```

## Idempotency

Pass 1 uses `skipExistingRecords: true` on TaxTreatment and TaxPolicy, so re-runs will skip existing records. Product2 Update will re-apply the same `TaxPolicyId`. Pass 2 updates Status fields, which should be idempotent (setting Active on already-Active records).

**Not yet validated** — idempotency testing against a 260 org is pending.

## 260 Schema Analysis (Confirmed via Org Describe)

Schema was queried against a 260 scratch org. Findings below.

### Polymorphic Fields

**None found.** All reference fields on tax objects are single-target lookups.

### Self-Referencing Fields

**None found.** No tax objects reference themselves.

### New Fields Found in 260 (Not in Current SOQL)

Significant schema additions across multiple objects:

**LegalEntity** — 5 new fields:

| Field                           | Type      | Updateable | Notes                                        |
|---------------------------------|-----------|------------|----------------------------------------------|
| `EmailTemplateId`               | REFERENCE | Yes        | Lookup to EmailTemplate — invoice email template |
| `ShouldAttachInvoiceDocToEmail` | BOOLEAN   | Yes        | Controls invoice PDF attachment on emails    |
| `LegalEntityLatitude`           | DOUBLE    | Yes        | Geo-location latitude                         |
| `LegalEntityLongitude`          | DOUBLE    | Yes        | Geo-location longitude                        |
| `LegalEntityGeocodeAccuracy`    | PICKLIST  | Yes        | Geo-coding accuracy level                     |

**TaxEngineProvider** — 2 new fields:

| Field                        | Type      | Updateable | Notes                                           |
|------------------------------|-----------|------------|--------------------------------------------------|
| `ApexAdapterId`              | REFERENCE | Yes        | Lookup to ApexClass — created by Apex script     |
| `CustomMetadataTypeApiName`  | STRING    | Yes        | Custom metadata type for engine configuration    |

**TaxEngine** — 10 new fields:

| Field                        | Type     | Updateable | Notes                                         |
|------------------------------|----------|------------|------------------------------------------------|
| `ExternalReference`          | STRING   | Yes        | External system reference identifier           |
| `TaxEngineStreet`            | TEXTAREA | Yes        | Address component                              |
| `TaxEngineCity`              | STRING   | Yes        | Address component                              |
| `TaxEngineState`             | STRING   | Yes        | Address component                              |
| `TaxEnginePostalCode`        | STRING   | Yes        | Address component                              |
| `TaxEngineLatitude`          | DOUBLE   | Yes        | Geo-location latitude                          |
| `TaxEngineLongitude`         | DOUBLE   | Yes        | Geo-location longitude                         |
| `Type`                       | PICKLIST | Yes        | Tax engine type classification                 |
| `TaxPrvdAccountIdentifier`   | STRING   | Yes        | Tax provider account identifier                |
| `ShouldCaptureTaxesAtHeader` | BOOLEAN  | Yes        | Controls header-level tax capture              |

**TaxTreatment** — 2 new fields:

| Field                       | Type      | Updateable | Notes                                        |
|-----------------------------|-----------|------------|----------------------------------------------|
| `ProductId`                 | REFERENCE | Yes        | Lookup to Product2 — product-specific tax treatment |
| `ShouldUseTaxTreatmentItems`| BOOLEAN   | Yes        | Enables tax treatment item sub-records        |

### Field Coverage Audit

| Object           | Status | Missing Fields                                                         |
|------------------|--------|------------------------------------------------------------------------|
| LegalEntity      | ⚠️     | 5 fields (email, invoice, geo — see above)                             |
| TaxEngineProvider| ⚠️     | 2 fields (ApexAdapterId created by script, CustomMetadataTypeApiName)  |
| TaxEngine        | ⚠️     | 10 fields (address, geo, type, provider ID, header tax capture)        |
| TaxTreatment     | ⚠️     | 2 fields (ProductId, ShouldUseTaxTreatmentItems)                       |
| TaxPolicy        | ✅     | All fields present (Name, Status, TreatmentSelection, Description, DefaultTaxTreatmentId) |
| Product2         | ✅     | Only updates TaxPolicyId — correct for this plan                       |

### Impact Assessment

The missing fields fall into three categories:

1. **Geo-location fields** (LegalEntity, TaxEngine): Address coordinates and geocode accuracy. Low priority — mainly needed for location-based tax calculation, not currently used by QB mock tax adapter.

2. **Email/Invoice fields** (LegalEntity): `EmailTemplateId` and `ShouldAttachInvoiceDocToEmail` control billing invoice email behavior. Medium priority — needed when billing email automation is configured.

3. **Functional fields** (TaxTreatment, TaxEngine): `ProductId` (product-specific tax treatment), `ShouldUseTaxTreatmentItems` (enables sub-records), `Type` and `ShouldCaptureTaxesAtHeader` (engine configuration). **High priority** — these enable new 260 tax features that may be required for advanced tax scenarios.

### Cross-Object Dependencies

| Lookup Target         | Source          | Status     |
|-----------------------|-----------------|------------|
| Product2              | qb-pcm          | Update only|
| TaxEngineProvider     | Apex script     | Created via REST API |
| TaxEngine             | Apex script     | Safety net upsert |
| LegalEntity           | This plan       | Upsert     |
| TaxPolicy             | This plan       | Upsert     |
| EmailTemplate         | Metadata deploy | Not in plan (new) |
| ApexClass             | Metadata deploy | Not in plan (set by script) |
| NamedCredential       | Metadata deploy | Not in plan |

## External ID / Composite Key Analysis (Confirmed via Org Describe)

### Schema-Enforced Unique Fields

| Object            | Field              | isUnique | isIdLookup | Current ExternalId Uses It? |
|-------------------|--------------------|----------|------------|------------------------------|
| TaxEngineProvider | `ApexAdapterId`    | **Yes**  | No         | No — uses `DeveloperName` (better choice) |
| TaxEngine         | `ExternalReference`| **Yes**  | Yes        | No — uses `TaxEngineName` (idLookup) |

**TaxEngine.ExternalReference** is schema-unique and could be used as an alternative externalId. However, `TaxEngineName` is the standard idLookup field and is more readable. No change recommended unless `ExternalReference` provides better cross-org portability.

**TaxEngineProvider.ApexAdapterId** is unique but it's a REFERENCE to ApexClass — not useful as a portable externalId. `DeveloperName` is the correct choice.

### ExternalId Assessment

| Object           | Current ExternalId              | Name Auto-Num | Unique? | Assessment |
|------------------|---------------------------------|---------------|---------|------------|
| LegalEntity      | `Name`                          | No            | No      | ✅ OK — human-readable, few records |
| TaxEngineProvider| `DeveloperName`                 | N/A (CMDT-like)| No     | ✅ OK — standard pattern for metadata types |
| TaxEngine        | `TaxEngineName`                 | N/A           | No      | ✅ OK — idLookup field |
| TaxTreatment     | `Name;LegalEntity.Name;TaxPolicy.Name` | No    | No      | ✅ OK — composite ensures uniqueness across entities/policies |
| TaxPolicy        | `Name`                          | No            | No      | ✅ OK — human-readable, 1 record |
| Product2         | `StockKeepingUnit`              | No*           | No*     | ✅ OK — platform-enforced unique when RLM enabled |

### Composite Key Complexity

All keys are simple (1-3 fields). No simplification opportunities. The `TaxTreatment` 3-field composite is necessary because the same treatment name could exist for different legal entities or policies.

## Optimization Opportunities

1. **Fix `excludeIdsFromCSVFiles`**: Change from `"false"` to `"true"` for portability — ensure all lookups use relationship traversal fields
2. **Add missing 260 fields to SOQL**: Prioritize `TaxTreatment.ProductId`, `TaxTreatment.ShouldUseTaxTreatmentItems`, `TaxEngine.Type`, `TaxEngine.ShouldCaptureTaxesAtHeader` for functional completeness
3. **Add geo and email fields**: Lower priority — add LegalEntity geo/email fields and TaxEngine address/geo fields for full schema coverage
4. **Add extraction support**: Create `extract_qb_tax_data` CCI task for bidirectional operation
5. **Clean up NamedCredential.csv**: Either add it to `export.json` or remove the orphaned file
6. **Consider combining activation**: Pass 2 (SFDMU) and `activateTaxRecords.apex` both activate TaxTreatment and TaxPolicy — consider simplifying to one activation mechanism
7. **API version management**: `createTaxEngine.apex` has a hardcoded `v66.0` — consider making this dynamic
