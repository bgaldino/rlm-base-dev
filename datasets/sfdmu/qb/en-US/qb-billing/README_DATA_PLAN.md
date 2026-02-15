# qb-billing SFDMU Data Plan

## Overview

The `qb-billing` data plan inserts and configures billing data for QuantumBit orgs using SFDMU
with a 3-pass approach. Activation of most record types is handled by dedicated Apex scripts
that run after the SFDMU passes complete (via the `prepare_billing` CCI flow).

## Platform Constraints

- Records with a `Status` field (`BillingPolicy`, `BillingTreatment`, `BillingTreatmentItem`,
  `PaymentTerm`) must be created in **Draft** status.
- Child records must be activated **before** parents:
  `BillingTreatmentItem` → `BillingTreatment` → `BillingPolicy`.
- Once a record moves out of Draft (Active or Inactive), it can **never** return to Draft and
  can **never** be deleted.
- A Draft `PaymentTerm` cannot be marked `IsDefault = true`; the default must be set
  simultaneously with activation.
- `BillingPolicy` cannot be activated unless its `DefaultBillingTreatmentId` references an
  Active `BillingTreatment` that belongs to that policy.
- `BillingTreatment` and `BillingPolicy` status transitions fail via SFDMU API updates due to
  platform validation rules; these activations require **Apex DML**.

## Folder Layout

```
qb-billing/
├── export.json                          # SFDMU config (3 object sets)
├── AccountingPeriod.csv                 # Pass 1 source (root)
├── BillingPolicy.csv                    # Pass 1 source (root)
├── BillingTreatment.csv                 # Pass 1 source (root)
├── BillingTreatmentItem.csv             # Pass 1 source (root)
├── GeneralLedgerAccount.csv             # Pass 1 source (root)
├── GeneralLedgerAcctAsgntRule.csv       # Pass 1 source (root)
├── LegalEntity.csv                      # Pass 1 source (root, Name only)
├── LegalEntyAccountingPeriod.csv        # Pass 1 source (root)
├── PaymentTerm.csv                      # Pass 1 source (root)
├── PaymentTermItem.csv                  # Pass 1 source (root)
├── Product2.csv                         # Pass 1 source (root)
├── objectset_source/
│   └── object-set-3/
│       ├── BillingTreatment.csv         # Pass 3 source (lookup reference, Draft)
│       └── BillingPolicy.csv            # Pass 3 source (set default treatment, Draft)
├── source/                              # Runtime only (populated by SFDMU)
├── target/                              # Runtime only (populated by SFDMU)
└── reports/                             # Runtime only (populated by SFDMU)
```

- **Pass 1** reads from the **plan root** (same directory as `export.json`). There is no
  `objectset_source/object-set-1/` directory.
- **Pass 2** has no separate source files; it queries the org for Draft `BillingTreatmentItem`
  records and updates their status.
- **Pass 3** reads from `objectset_source/object-set-3/`.
- `source/`, `target/`, and `reports/` are runtime artifacts created by SFDMU each execution.
  They are not part of the plan and should not be version-controlled.

## SFDMU Passes (export.json)

### Pass 1 — Insert/Upsert with Draft Status

Creates all records in Draft status with correct lookups:

| Object | Operation | External ID | Notes |
|--------|-----------|-------------|-------|
| `AccountingPeriod` | Upsert | `Name;FinancialYear` | |
| `LegalEntity` | Upsert | `Name` | Root CSV has `Name` only; other fields come from qb-tax |
| `LegalEntyAccountingPeriod` | Upsert | `Name` | |
| `PaymentTerm` | Upsert | `Name` | `IsDefault=false` for all; `skipExistingRecords` |
| `PaymentTermItem` | Upsert | `$$PaymentTerm.Name$Type` | `skipExistingRecords` |
| `BillingPolicy` | Upsert | `Name` | No `DefaultBillingTreatmentId` yet; `skipExistingRecords` |
| `BillingTreatment` | Upsert | `Name;BillingPolicy.Name;LegalEntity.Name` | Composite external ID; `skipExistingRecords` |
| `BillingTreatmentItem` | Upsert | `$$Name$BillingTreatment.Name` | `skipExistingRecords` |
| `Product2` | Update | `StockKeepingUnit` | Sets `BillingPolicyId` on existing products |
| `GeneralLedgerAccount` | Upsert | `Name;LegalEntity.Name` | |
| `GeneralLedgerAcctAsgntRule` | Upsert | `Name;LegalEntity.Name` | |

Key lookup resolution:
- `BillingTreatment` query includes `BillingPolicy.Name` and `LegalEntity.Name` for composite
  external ID matching and parent lookup resolution.
- `BillingTreatmentItem` query includes `BillingTreatment.Name`,
  `BillingTreatment.BillingPolicy.Name`, and `BillingTreatment.LegalEntity.Name` for
  grandparent composite lookup resolution.
- `GeneralLedgerAccount` and `GeneralLedgerAcctAsgntRule` queries include `LegalEntity.Name`.

### Pass 2 — Activate BillingTreatmentItem

Updates Draft `BillingTreatmentItem` records to Active status via SFDMU API. This is the
only object activated by SFDMU directly; the platform allows status updates on
`BillingTreatmentItem` via the standard API.

| Object | Operation | External ID | Query Filter |
|--------|-----------|-------------|-------------|
| `BillingTreatmentItem` | Update | `$$Name$BillingTreatment.Name` | `WHERE Status = 'Draft'` |

### Pass 3 — Set DefaultBillingTreatmentId on BillingPolicy

Sets the `DefaultBillingTreatmentId` lookup on BillingPolicy records while they are still in
Draft status. `BillingTreatment` is included (not for update) so SFDMU can resolve the
composite lookup.

| Object | Operation | External ID | Query Filter | Purpose |
|--------|-----------|-------------|-------------|---------|
| `BillingTreatment` | Update | `Name;BillingPolicy.Name;LegalEntity.Name` | `WHERE Status = 'Draft'` | Loaded for lookup resolution |
| `BillingPolicy` | Update | `Name` | `WHERE Status = 'Draft'` | Sets `DefaultBillingTreatmentId` via composite `$$Name$BillingPolicy.Name$LegalEntity.Name` |

## Activation (Apex Scripts)

After SFDMU completes all 3 passes, the `prepare_billing` CCI flow runs these Apex tasks:

### 1. `activate_default_payment_term`

Script: `scripts/apex/activateDefaultPaymentTerm.apex`

1. Finds "Default Payment Term", sets `IsDefault = true` and `Status = Active`.
2. Activates all remaining Draft `PaymentTerm` records (e.g., "Net 45").

### 2. `activate_billing_records`

Script: `scripts/apex/activateBillingRecords.apex`

1. Activates all non-Active `BillingTreatmentItem` (safety net; Pass 2 should have done this).
2. Activates `BillingTreatment` records that have at least one Active `BillingTreatmentItem`.
3. Activates `BillingPolicy` records whose `DefaultBillingTreatmentId` references an Active
   `BillingTreatment` belonging to that policy.

## Re-run Safety

The plan is designed to be safely re-run against an org that already has Active billing records:

- **`skipExistingRecords: true`** on `PaymentTerm`, `PaymentTermItem`, `BillingPolicy`,
  `BillingTreatment`, and `BillingTreatmentItem` in Pass 1. SFDMU matches by external ID
  and skips records that already exist (regardless of their status).
- **`WHERE Status = 'Draft'`** filters in Pass 2 and Pass 3 mean those passes only process
  records that haven't been activated yet. If all records are already Active, these passes
  are effectively no-ops.
- Apex activation scripts use `WHERE Status != 'Active'` or `WHERE Status = 'Draft'`, so
  already-Active records are left untouched.

## prepare_billing CCI Flow

The full `prepare_billing` flow (defined in `cumulusci.yml`) runs these steps:

1. `insert_billing_data` — SFDMU 3-pass data load (scratch org) or `insert_billing_data_prod` (non-scratch)
2. `activate_flow` — Activates `RLM_Order_to_Billing_Schedule_Flow`
3. `activate_default_payment_term` — Apex: activates PaymentTerms
4. `activate_billing_records` — Apex: activates BillingTreatmentItem → BillingTreatment → BillingPolicy
5. `deploy_post_billing` — Deploys post-billing metadata

## Utility Tasks

These standalone tasks are available for debugging and cleanup but are not part of the
`prepare_billing` flow:

| Task | Script | Description |
|------|--------|-------------|
| `query_billing_state` | `scripts/apex/query_billing_state.apex` | Queries and logs all billing record states (check debug logs for output) |
| `validate_billing_structure` | `scripts/apex/validateBillingStructure.apex` | Fails if any `BillingTreatment` has null `BillingPolicyId` |
| `delete_draft_billing_records` | `scripts/apex/deleteDraftBillingRecords.apex` | Deletes Draft billing records in dependency order (only Draft records; Active records are never touched) |
