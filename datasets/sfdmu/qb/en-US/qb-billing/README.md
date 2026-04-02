# qb-billing Data Plan

SFDMU data plan for QuantumBit (QB) billing configuration. Creates accounting periods, legal entities, legal entity accounting period mappings, payment terms, billing policies/treatments/items, general ledger accounts, GL assignment rules, and assigns billing policies to products. Uses a 3-pass architecture with Apex activation for complex dependency ordering.

## CCI Integration

### Flow: `prepare_billing`

This plan is executed as **step 1** of the `prepare_billing` flow (when `billing=true`, `qb=true`, `refresh=false`).

| Step | Task                              | When           | Description                                                                             |
|------|-----------------------------------|----------------|-----------------------------------------------------------------------------------------|
| 1    | `insert_billing_data`             | billing+qb     | Runs this SFDMU plan (3 passes)                                                         |
| 2    | `insert_q3_billing_data`          | billing+q3     | Loads Q3 billing data (gated by q3 flag)                                                |
| 3    | `activate_flow`                   | billing        | Activates `RLM_Order_to_Billing_Schedule_Flow`                                          |
| 4    | `activate_default_payment_term`   | billing        | Runs `activateDefaultPaymentTerm.apex`                                                  |
| 5    | `activate_billing_records`        | billing        | Runs `activateBillingRecords.apex` (BTI → BT → BP)                                     |
| 6    | `enable_timeline`                 | billing_ui     | Enables industries_common:timeline (required before billing_ui flexipages)               |
| 7    | `deploy_post_billing`             | billing        | Deploys billing settings/metadata from `unpackaged/post_billing`                        |
| 8    | `deploy_billing_id_settings`      | billing        | Deploys `post_billing_id_settings` — sets GL accounts, legal entity, treatment, tax IDs |
| 9    | `deploy_billing_template_settings`| billing        | Re-enables Invoice Email/PDF toggles (cycled off in step 8 to avoid template ID errors) |
| 10   | `deploy_post_billing_ui`          | billing_ui     | Deploys Billing UI LWC components, Apex, fields, permset from `unpackaged/post_billing_ui` |
| 11   | `assign_permission_sets`          | billing_ui     | Assigns `RLM_BillingUI` permission set to the running user                              |
| 12   | `apply_context_billing_order`     | billing+billing_ui | Patches `RLM_BillingContext` Order node — maps `BillingArrangement__std` → `RLM_Billing_Arrangement__c` and `BillingProfile__std` → `RLM_Billing_Profile__c` |

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
| 1  | AccountingPeriod             | Upsert    | `Name;FinancialYear`                       | 84      |
| 2  | LegalEntity                  | Upsert    | `Name`                                     | 2       |
| 3  | LegalEntyAccountingPeriod    | Upsert    | `Name`                                     | 168     |
| 4  | PaymentTerm                  | Upsert    | `Name`                                     | 2       |
| 5  | PaymentTermItem              | Upsert    | `PaymentTerm.Name;Type`                    | 2       |
| 6  | BillingPolicy                | Upsert    | `Name`                                     | 3       |
| 7  | BillingTreatment             | Upsert    | `Name`                                     | 5       |
| 8  | BillingTreatmentItem         | Upsert    | `Name;BillingTreatment.Name`               | 8       |
| 9  | Product2                     | Update    | `StockKeepingUnit`                         | 164     |
| 10 | GeneralLedgerAccount         | Upsert    | `AccountingCode`                           | 51      |
| 11 | GeneralLedgerAcctAsgntRule   | Upsert    | `Name`                                     | 8       |
| 12 | PaymentRetryRuleSet          | Upsert    | `Name`                                     | 1       |
| 13 | PaymentRetryRule             | Upsert    | `PaymentGatewayErrorCategory;PaymentRetryRuleSet.Name;RetryIntervalType` | 6 |

**Note:** PaymentTerm, PaymentTermItem, BillingPolicy, BillingTreatment, and BillingTreatmentItem all use `skipExistingRecords: true` to avoid overwriting existing records. Product2 is Update-only (sets `BillingPolicyId`). See [Optimization Opportunities](#optimization-opportunities) for known issues with `skipExistingRecords`.

**FK ID pattern:** All parent-lookup fields include both the FK ID field (e.g. `PaymentTermId`, `BillingTreatmentId`, `BillingPolicyId`, `LegalEntityId`) in the SOQL SELECT and the traversal column (e.g. `PaymentTerm.Name`, `BillingTreatment.Name`) in the CSV header. SFDMU v5 requires the FK ID in the SELECT to know which field to write; the traversal column in the CSV provides the lookup value. Omitting the FK ID results in null FKs even when the traversal column resolves correctly.

### Pass 2 — Activate BillingTreatmentItem

| # | Object              | Operation | External ID                    | Records |
|---|---------------------|-----------|--------------------------------|---------|
| 1 | BillingTreatmentItem| Update    | `Name;BillingTreatment.Name`   | (Draft) |

Activates BillingTreatmentItem records that are still in Draft status.

### Pass 3 — Activate BillingTreatment and Set BillingPolicy Defaults

| # | Object           | Operation | External ID | Records |
|---|------------------|-----------|-------------|---------|
| 1 | BillingTreatment | Update    | `Name`      | (Draft) |
| 2 | BillingPolicy    | Update    | `Name`      | (Draft) |

Activates BillingTreatment records and sets `DefaultBillingTreatmentId` on BillingPolicy. BillingPolicy.csv includes a `DefaultBillingTreatment.Name` traversal column so SFDMU can resolve the FK at load time.

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

AccountingPeriod (84 monthly periods for 2024-2030), LegalEntity (US and Canada), and their mapping via LegalEntyAccountingPeriod (168 records = 84 periods x 2 entities).

### Payment Terms (Objects 4-5)

PaymentTerm records with PaymentTermItem definitions (linked via `$$PaymentTerm.Name$Type` composite key).

### Billing Policy Chain (Objects 6-8)

Three-level hierarchy: BillingPolicy -> BillingTreatment -> BillingTreatmentItem. The activation requires strict bottom-up ordering (BTI first, then BT, then BP with default treatment set).

### General Ledger (Objects 10-11)

Chart of accounts (51 GL accounts) with 8 assignment rules mapping transaction types to debit/credit accounts per legal entity.

## Composite External IDs

| Object               | Composite Key                                                            | CSV `$$` Column |
|----------------------|--------------------------------------------------------------------------|-----------------|
| AccountingPeriod     | `Name;FinancialYear`                                                     | Yes             |
| PaymentTermItem      | `PaymentTerm.Name;Type`                                                  | Yes             |
| BillingTreatmentItem | `Name;BillingTreatment.Name`                                             | Yes             |
| PaymentRetryRule     | `PaymentGatewayErrorCategory;PaymentRetryRuleSet.Name;RetryIntervalType` | Yes             |

GL assignment rules reference debit/credit accounts via `DebitGeneralLedgerAccount.AccountingCode` and `CreditGeneralLedgerAccount.AccountingCode` traversal columns in the CSV (resolved to `CreditGeneralLedgerAccountId`/`DebitGeneralLedgerAccountId` FK IDs in SELECT).

## Portability

All external IDs use portable, human-readable fields:

- **Name** fields: All human-readable (e.g., "Default Legal Entity - US", "Default Payment Term", "Billing Treatment Item - Advance - USA", "1100 Accounts Receivable - Trade")
- **LegalEntyAccountingPeriod.Name**: Descriptive composite strings (e.g., "Default Legal Entity - US-2024-January1-January31")
- **StockKeepingUnit** for Product2 references
- **No auto-numbered Name fields**

## Billing Context Plan (`apply_context_billing_order`)

Step 12 of `prepare_billing` patches the `RLM_BillingContext` context definition using the plan at `datasets/context_plans/Billing/contexts/billing_order_attributes.json`. It adds two attribute mappings to the `OrderEntitiesMapping` mapping on the `BillingTransaction` node:

| Context Attribute         | sObject | sObjectField               | Purpose |
|---------------------------|---------|----------------------------|---------|
| `BillingArrangement__std` | Order   | `RLM_Billing_Arrangement__c` | Maps billing arrangement lookup from Order to BillingTransaction context |
| `BillingProfile__std`     | Order   | `RLM_Billing_Profile__c`    | Maps billing profile lookup from Order to BillingTransaction context |

**Notes:**
- `SavedPaymentMethod__std` is intentionally excluded — the platform already has an inherited mapping for this attribute; adding a custom one fails with `INVALID_INPUT: An Inherited mapping for ContextAttribute: SavedPaymentMethod already exists.`
- Task verification logs `hasHydrationDetail: false` for both `__std` attributes — this is a **known false negative**. The Connect API GET does not expose hydration records for `__std` attributes in `contextAttrHydrationDetailList`; the records exist and are confirmed via Tooling API.
- Step 12 is gated by `billing AND billing_ui` because `RLM_Billing_Arrangement__c` and `RLM_Billing_Profile__c` are Order fields deployed by `post_billing_ui` (step 10).

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
├── export.json                          # SFDMU data plan (3 passes, 16 objects)
├── README.md                            # This file
│
│  Source CSVs (Pass 1 - Draft status)
├── AccountingPeriod.csv                 # 84 records (2024–2030)
├── LegalEntity.csv                      # 2 records
├── LegalEntyAccountingPeriod.csv        # 168 records (84 periods x 2 entities)
├── PaymentTerm.csv                      # 2 records
├── PaymentTermItem.csv                  # 2 records
├── BillingPolicy.csv                    # 3 records
├── BillingTreatment.csv                 # 5 records
├── BillingTreatmentItem.csv             # 8 records
├── Product2.csv                         # 164 records (Update only)
├── GeneralLedgerAccount.csv             # 51 records
├── GeneralLedgerAcctAsgntRule.csv       # 8 records
├── PaymentRetryRuleSet.csv
├── PaymentRetryRule.csv
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

**Validated** — `test_qb_billing_idempotency` passes on Release 260. All 13 objects confirmed idempotent.

## 260 Schema Analysis (Confirmed via Org Describe)

Schema was queried against a 260 scratch org. Findings below.

### Polymorphic Fields

**None found.** All reference fields on billing objects are single-target lookups.

### Self-Referencing Fields

**None found.** No billing objects reference themselves.

### New Fields Found in 260 (Not in Current SOQL)

| Object                     | Field                       | Type     | Updateable | Notes                                           |
|----------------------------|-----------------------------|----------|------------|--------------------------------------------------|
| **BillingTreatment**       | `CanChangeBillingFrequency` | BOOLEAN  | Yes        | Allows billing frequency changes post-creation — **added to plan** |
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
| BillingTreatment           | ✅     | `CanChangeBillingFrequency` added                            |
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

| Object               | Field            | isUnique | isIdLookup | ExternalId |
|----------------------|------------------|----------|------------|------------|
| GeneralLedgerAccount | `AccountingCode` | **Yes**  | Yes        | `AccountingCode` ✅ |

### ExternalId Assessment

| Object                     | ExternalId                                                               | Name Auto-Num | Assessment |
|----------------------------|--------------------------------------------------------------------------|---------------|------------|
| AccountingPeriod           | `Name;FinancialYear`                                                     | No            | ✅ 2 fields necessary (period name + year) |
| LegalEntity                | `Name`                                                                   | No            | ✅ Human-readable |
| LegalEntyAccountingPeriod  | `Name`                                                                   | No (read-only)| ✅ Descriptive composite string |
| PaymentTerm                | `Name`                                                                   | No            | ✅ Human-readable |
| PaymentTermItem            | `PaymentTerm.Name;Type`                                                  | **Yes**        | ✅ Composite from parent + type |
| BillingPolicy              | `Name`                                                                   | No            | ✅ Human-readable |
| BillingTreatment           | `Name`                                                                   | No            | ✅ Unique within org |
| BillingTreatmentItem       | `Name;BillingTreatment.Name`                                             | No            | ✅ Composite from parent |
| GeneralLedgerAccount       | `AccountingCode`                                                         | No (read-only)| ✅ Schema-enforced unique |
| GeneralLedgerAcctAsgntRule | `Name`                                                                   | No            | ✅ Names are unique in this dataset |
| PaymentRetryRule           | `PaymentGatewayErrorCategory;PaymentRetryRuleSet.Name;RetryIntervalType` | No            | ✅ Composite uniqueness |
| Product2                   | `StockKeepingUnit`                                                       | No*           | ✅ Platform-enforced unique when RLM enabled |

## Optimization Opportunities

1. **Simplify activation**: The 3-pass SFDMU activation + 2 Apex activation scripts is complex — consider whether the Apex scripts alone could handle all activation, reducing to a simpler 1-pass SFDMU plan
2. **LegalEntity field gap**: Same missing geo/email fields as qb-tax — coordinate update across both plans
3. **Investigate `skipExistingRecords` behavior**: PaymentTerm, PaymentTermItem, BillingPolicy, BillingTreatment, and BillingTreatmentItem use `skipExistingRecords: true`. This prevents overwriting existing records but may silently skip new records added to the CSV if any existing record is already present. The exact SFDMU v5 behavior of `skipExistingRecords` — whether it skips the entire object or only matched records — needs verification. If it skips the whole object when any record exists, new CSV rows will never load after initial install.
