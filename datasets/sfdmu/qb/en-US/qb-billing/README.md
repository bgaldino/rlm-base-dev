# qb-billing Data Plan

SFDMU data plan for QuantumBit (QB) billing configuration. Creates accounting periods, legal entities, legal entity accounting period mappings, payment terms, billing policies/treatments/items, general ledger accounts, GL assignment rules, and assigns billing policies to products. Uses a 3-pass architecture with Apex activation for complex dependency ordering.

## CCI Integration

### Flow: `prepare_billing`

This plan is executed as **step 1** of the `prepare_billing` flow (when `billing=true`, `qb=true`, `refresh=false`).

| Step | Task                           | Description                                                    |
|------|--------------------------------|----------------------------------------------------------------|
| 1    | `insert_billing_data`          | Runs this SFDMU plan (3 passes)                                |
| 3    | `activate_flow`                | Activates `RLM_Order_to_Billing_Schedule_Flow`                 |
| 4    | `activate_default_payment_term`| Runs `activateDefaultPaymentTerm.apex`                         |
| 5    | `activate_billing_records`     | Runs `activateBillingRecords.apex`                             |
| 6    | `deploy_post_billing`          | Deploys billing metadata from `unpackaged/post_billing`        |

### Task Definition

```yaml
insert_billing_data:
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-billing"
```

## Data Plan Overview

The plan uses **3 SFDMU passes** followed by **Apex activation**:

```
Pass 1 (SFDMU)           Pass 2 (SFDMU)          Pass 3 (SFDMU)           Apex Activation
──────────────────       ─────────────────       ─────────────────        ─────────────────
Insert all objects  ->   Activate BTI        ->  Activate BT          ->  activateDefaultPaymentTerm.apex
in Draft status          (BillingTreatmentItem)  + set BillingPolicy       activateBillingRecords.apex
+ assign BillingPolicy                            DefaultBillingTreatment  (BTI -> BT -> BP activation)
to Product2
```

### Pass 1 — Insert/Upsert with Draft Status

| #  | Object                       | Operation | External ID                                | Records |
|----|------------------------------|-----------|--------------------------------------------|---------|
| 1  | AccountingPeriod             | Upsert    | `Name;FinancialYear`                       | 24      |
| 2  | LegalEntity                  | Upsert    | `Name`                                     | 2       |
| 3  | LegalEntyAccountingPeriod    | Upsert    | `Name`                                     | 48      |
| 4  | PaymentTerm                  | Upsert    | `Name`                                     | 2       |
| 5  | PaymentTermItem              | Upsert    | `$$PaymentTerm.Name$Type`                  | 2       |
| 6  | BillingPolicy                | Upsert    | `Name`                                     | 3       |
| 7  | BillingTreatment             | Upsert    | `Name;BillingPolicy.Name;LegalEntity.Name` | 5       |
| 8  | BillingTreatmentItem         | Upsert    | `$$Name$BillingTreatment.Name`             | 8       |
| 9  | Product2                     | Update    | `StockKeepingUnit`                         | 164     |
| 10 | GeneralLedgerAccount         | Upsert    | `Name;LegalEntity.Name`                    | 51      |
| 11 | GeneralLedgerAcctAsgntRule   | Upsert    | `Name;LegalEntity.Name`                    | 8       |

**Note:** PaymentTerm, PaymentTermItem, BillingPolicy, BillingTreatment, and BillingTreatmentItem all use `skipExistingRecords: true` to avoid overwriting existing records. Product2 is Update-only (sets `BillingPolicyId`).

### Pass 2 — Activate BillingTreatmentItem

| # | Object              | Operation | External ID                    | Records |
|---|---------------------|-----------|--------------------------------|---------|
| 1 | BillingTreatmentItem| Update    | `$$Name$BillingTreatment.Name` | (Draft) |

Activates BillingTreatmentItem records that are still in Draft status.

### Pass 3 — Activate BillingTreatment and Set BillingPolicy Defaults

| # | Object           | Operation | External ID                                | Records |
|---|------------------|-----------|--------------------------------------------|---------|
| 1 | BillingTreatment | Update    | `Name;BillingPolicy.Name;LegalEntity.Name` | (Draft) |
| 2 | BillingPolicy    | Update    | `Name`                                     | (Draft) |

Activates BillingTreatment records and sets `DefaultBillingTreatmentId` on BillingPolicy. The BillingPolicy query uses a nested `$$` column for the default treatment lookup: `DefaultBillingTreatment.$$Name$BillingPolicy.Name$LegalEntity.Name`.

## Apex Activation Scripts

### `activateDefaultPaymentTerm.apex`

Activates payment terms in order:
1. Activate "Default Payment Term" and set `IsDefault = true`
2. Activate all remaining Draft PaymentTerm records

### `activateBillingRecords.apex`

Activates billing records in strict dependency order:
1. **BillingTreatmentItem** -> `Status = 'Active'` (all non-Active)
2. **BillingTreatment** -> `Status = 'Active'` (only those with at least one Active BTI)
3. **BillingPolicy** -> `Status = 'Active'` (only when DefaultBillingTreatment is Active and belongs to this policy)

Both scripts are idempotent — all queries filter on non-Active status.

## Configuration

### Notable Settings

- **`excludeIdsFromCSVFiles: "true"`** — Portable, no raw Salesforce IDs in CSVs
- **`useSeparatedCSVFiles: true`** — SFDMU uses `objectset_source/` subdirectories for pass-specific CSV overrides
- **`skipExistingRecords: true`** on billing objects — prevents overwriting existing billing config

## Key Object Groups

### Financial Infrastructure (Objects 1-3)

AccountingPeriod (24 monthly periods for 2024-2025), LegalEntity (US and Canada), and their mapping via LegalEntyAccountingPeriod (48 records = 24 periods x 2 entities).

### Payment Terms (Objects 4-5)

PaymentTerm records with PaymentTermItem definitions (linked via `$$PaymentTerm.Name$Type` composite key).

### Billing Policy Chain (Objects 6-8)

Three-level hierarchy: BillingPolicy -> BillingTreatment -> BillingTreatmentItem. The activation requires strict bottom-up ordering (BTI first, then BT, then BP with default treatment set).

### General Ledger (Objects 10-11)

Chart of accounts (51 GL accounts) with 8 assignment rules mapping transaction types to debit/credit accounts per legal entity.

## Composite External IDs

| Object                     | Composite Key                                    | CSV `$$` Column |
|----------------------------|--------------------------------------------------|-----------------|
| AccountingPeriod           | `Name;FinancialYear`                             | Yes             |
| PaymentTermItem            | `PaymentTerm.Name;Type`                          | Yes             |
| BillingTreatment           | `Name;BillingPolicy.Name;LegalEntity.Name`       | Yes             |
| BillingTreatmentItem       | `Name;BillingTreatment.Name`                     | Yes             |
| GeneralLedgerAccount       | `Name;LegalEntity.Name`                          | Yes             |
| GeneralLedgerAcctAsgntRule | `Name;LegalEntity.Name`                          | Yes             |

GL assignment rules also use nested `$$` columns for debit/credit account lookups: `DebitGeneralLedgerAccount.$$Name$LegalEntity.Name` and `CreditGeneralLedgerAccount.$$Name$LegalEntity.Name`.

## Portability

All external IDs use portable, human-readable fields:

- **Name** fields: All human-readable (e.g., "Default Legal Entity - US", "Default Payment Term", "Billing Treatment Item - Advance - USA", "1100 Accounts Receivable - Trade")
- **LegalEntyAccountingPeriod.Name**: Descriptive composite strings (e.g., "Default Legal Entity - US-2024-January1-January31")
- **StockKeepingUnit** for Product2 references
- **No auto-numbered Name fields**

## Dependencies

**Upstream:**
- **qb-pcm** — Product2 records must exist (matched by `StockKeepingUnit`)
- **qb-tax** — LegalEntity records (shared between tax and billing — billing creates them too via Upsert)

**Downstream:**
- **qb-rating** — UsageResourceBillingPolicy may reference billing infrastructure
- Runtime billing/invoicing engine consumes this configuration

## File Structure

```
qb-billing/
├── export.json                          # SFDMU data plan (3 passes, 14 objects)
├── README.md                            # This file
│
│  Source CSVs (Pass 1 - Draft status)
├── AccountingPeriod.csv                 # 24 records
├── LegalEntity.csv                      # 2 records
├── LegalEntyAccountingPeriod.csv        # 48 records
├── PaymentTerm.csv                      # 2 records
├── PaymentTermItem.csv                  # 2 records
├── BillingPolicy.csv                    # 3 records
├── BillingTreatment.csv                 # 5 records
├── BillingTreatmentItem.csv             # 8 records
├── Product2.csv                         # 164 records (Update only)
├── GeneralLedgerAccount.csv             # 51 records
├── GeneralLedgerAcctAsgntRule.csv       # 8 records
│
│  Source CSVs (Pass 2 - Activate BTI)
├── objectset_source/
│   └── object-set-2/
│       └── BillingTreatmentItem.csv     # BTI records (Status -> Active)
│
│  Source CSVs (Pass 3 - Activate BT + BP defaults)
├── objectset_source/
│   └── object-set-3/
│       ├── BillingTreatment.csv         # BT records (Status -> Active)
│       └── BillingPolicy.csv            # BP records (DefaultBillingTreatment + Status)
│
│  SFDMU Runtime (gitignored)
├── source/                              # SFDMU-generated source snapshots
├── target/                              # SFDMU-generated target snapshots
└── reports/                             # SFDMU reports
```

## Idempotency

Pass 1 uses `skipExistingRecords: true` on billing objects, so re-runs will skip existing records. Passes 2 and 3 update Status and DefaultBillingTreatment fields with `WHERE Status = 'Draft'` filters, so they are no-ops on already-activated records.

The Apex activation scripts filter on `Status != 'Active'`, making them idempotent.

**Not yet validated** — idempotency testing against a 260 org is pending.

## 260 Schema Analysis (Confirmed via Org Describe)

Schema was queried against a 260 scratch org. Findings below.

### Polymorphic Fields

**None found.** All reference fields on billing objects are single-target lookups.

### Self-Referencing Fields

**None found.** No billing objects reference themselves.

### New Fields Found in 260 (Not in Current SOQL)

| Object                     | Field                       | Type     | Updateable | Notes                                           |
|----------------------------|-----------------------------|----------|------------|--------------------------------------------------|
| **BillingTreatment**       | `CanChangeBillingFrequency` | BOOLEAN  | Yes        | Allows billing frequency changes post-creation   |
| **LegalEntyAccountingPeriod** | `ClosureStage`           | PICKLIST | Yes        | Accounting period closure tracking               |

### Field Coverage Audit

| Object                     | Status | Notes                                                        |
|----------------------------|--------|--------------------------------------------------------------|
| AccountingPeriod           | ✅     | All 5 key fields present; `Total*Amount` fields omitted (zero for new orgs) |
| LegalEntity                | ⚠️     | Same missing fields as qb-tax (email, geo) — see qb-tax README |
| LegalEntyAccountingPeriod  | ⚠️     | Minor: `ClosureStage` not in SOQL (low priority)             |
| PaymentTerm                | ✅     | All 4 fields present                                         |
| PaymentTermItem            | ✅     | All fields present                                           |
| BillingPolicy              | ✅     | All fields present (including DefaultBillingTreatmentId in Pass 3) |
| BillingTreatment           | ⚠️     | Missing `CanChangeBillingFrequency` (new boolean)            |
| BillingTreatmentItem       | ✅     | All fields present; `Handling0Amount` confirmed valid in 260  |
| Product2                   | ✅     | Only updates BillingPolicyId — correct for this plan         |
| GeneralLedgerAccount       | ✅     | All fields present                                           |
| GeneralLedgerAcctAsgntRule | ✅     | All fields present                                           |

### Impact Assessment

- **`BillingTreatment.CanChangeBillingFrequency`**: New boolean controlling whether the billing frequency can be changed after creation. **Medium priority** — affects billing flexibility configuration. Default is likely `false`, so existing data loads may work without it, but extractions from orgs where this is `true` would lose the value.
- **`LegalEntyAccountingPeriod.ClosureStage`**: Controls the closure tracking stage for legal entity accounting periods. **Low priority** — only relevant when period-end close processes are configured.
- **`LegalEntity` geo/email fields**: Same as qb-tax — 5 missing fields (see qb-tax analysis).

### Cross-Object Dependencies

| Lookup Target           | Source        | Status     |
|-------------------------|---------------|------------|
| Product2                | qb-pcm        | Update only|
| LegalEntity             | This plan     | Upsert (shared with qb-tax) |
| AccountingPeriod        | This plan     | Upsert     |
| PaymentTerm             | This plan     | Upsert     |
| BillingPolicy           | This plan     | Upsert     |
| BillingTreatment        | This plan     | Upsert     |
| GeneralLedgerAccount    | This plan     | Upsert     |

## External ID / Composite Key Analysis (Confirmed via Org Describe)

### Schema-Enforced Unique Fields

| Object               | Field            | isUnique | isIdLookup | Current ExternalId Uses It? |
|----------------------|------------------|----------|------------|------------------------------|
| GeneralLedgerAccount | `AccountingCode` | **Yes**  | Yes        | **No** — uses `Name;LegalEntity.Name` |

### Simplification Opportunity: GeneralLedgerAccount

`GeneralLedgerAccount.AccountingCode` is **schema-enforced unique**. The current externalId is `Name;LegalEntity.Name` (2-field composite), but since `AccountingCode` alone guarantees uniqueness, both components are **redundant**. This simplification would:
- Reduce the composite key to a single field
- Remove the need for `$$` composite key columns
- Simplify the GeneralLedgerAcctAsgntRule lookups (`DebitGeneralLedgerAccount.$$Name$LegalEntity.Name` and `CreditGeneralLedgerAccount.$$Name$LegalEntity.Name` could become `DebitGeneralLedgerAccount.AccountingCode` and `CreditGeneralLedgerAccount.AccountingCode`)

**Recommendation:** Simplify GeneralLedgerAccount externalId from `Name;LegalEntity.Name` to just `AccountingCode`. This cascades to simplify GeneralLedgerAcctAsgntRule's debit/credit account lookups.

### ExternalId Assessment

| Object                     | Current ExternalId                               | Name Auto-Num | Assessment |
|----------------------------|--------------------------------------------------|---------------|------------|
| AccountingPeriod           | `Name;FinancialYear`                             | No            | ✅ OK — 2 fields necessary (period name + year) |
| LegalEntity                | `Name`                                           | No            | ✅ OK — human-readable |
| LegalEntyAccountingPeriod  | `Name`                                           | No (read-only)| ✅ OK — descriptive composite string |
| PaymentTerm                | `Name`                                           | No            | ✅ OK — human-readable |
| PaymentTermItem            | `$$PaymentTerm.Name$Type`                        | **Yes**        | ✅ Good — composite from parent + type |
| BillingPolicy              | `Name`                                           | No            | ✅ OK — human-readable |
| BillingTreatment           | `Name;BillingPolicy.Name;LegalEntity.Name`       | No            | ✅ OK — 3-field composite for cross-entity uniqueness |
| BillingTreatmentItem       | `$$Name$BillingTreatment.Name`                   | No            | ✅ OK — composite from parent |
| GeneralLedgerAccount       | `Name;LegalEntity.Name`                          | No (read-only)| ⚠️ Can simplify to `AccountingCode` (schema-unique) |
| GeneralLedgerAcctAsgntRule | `Name;LegalEntity.Name`                          | No            | ✅ OK — 2-field composite |
| Product2                   | `StockKeepingUnit`                               | No*           | ✅ OK — platform-enforced unique when RLM enabled |

### Composite Key Complexity

All keys are relatively simple (1-3 fields). The main simplification opportunity is GeneralLedgerAccount (see above), which cascades to simplify the GL Assignment Rule lookups.

## Optimization Opportunities

1. **Simplify GeneralLedgerAccount externalId**: `AccountingCode` is schema-unique — replace `Name;LegalEntity.Name` composite and cascade simplification to GL Assignment Rule debit/credit lookups
2. **Add `CanChangeBillingFrequency` to BillingTreatment SOQL**: New 260 field needed for complete billing treatment configuration
3. **Add extraction support**: Create `extract_qb_billing_data` CCI task for bidirectional operation
4. **Review CSVIssuesReport**: Investigate the 10-line CSVIssuesReport.csv for any existing data quality issues
5. **Simplify activation**: The 3-pass SFDMU activation + 2 Apex activation scripts is complex — consider whether the Apex scripts alone could handle all activation, reducing to a simpler 1-pass SFDMU plan
6. **Extend accounting periods**: Current periods cover 2024-2025 only — may need extension for longer-running orgs
7. **LegalEntity field gap**: Same missing geo/email fields as qb-tax — coordinate update across both plans
8. **Consider `excludeIdsFromCSVFiles` consistency**: Already set to `"true"` — good for portability (unlike qb-tax which uses `"false"`)
