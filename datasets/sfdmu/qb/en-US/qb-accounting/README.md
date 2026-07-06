# qb-accounting Data Plan

SFDMU data plan for QuantumBit (QB) general ledger accounting configuration: GL accounts, GL account assignment rules, GL journal entry rules, and billing batch filter criteria.

> **Status: NOT wired to any CCI task.** This plan is dormant — no `cumulusci.yml`
> task references `datasets/sfdmu/qb/en-US/qb-accounting`. It exists as a
> standalone SFDMU plan only. Wiring it into a task/flow (e.g. an
> `insert_qb_accounting_data` task under `prepare_billing`) is a separate
> decision, not part of this change.

## Data Plan Overview

Single-pass plan, 4 objects, ordered parent → child:

| # | Object                        | Operation | External ID                        | Records |
|---|--------------------------------|-----------|-------------------------------------|---------|
| 1 | GeneralLedgerAccount           | Upsert    | `AccountingCode`                    | 51      |
| 2 | GeneralLedgerAcctAsgntRule     | Upsert    | `Name`                              | 8       |
| 3 | GeneralLedgerJrnlEntryRule     | Upsert    | `JournalEntryRuleName`              | 0 (header-only CSV) |
| 4 | BillingBatchFilterCriteria     | Upsert    | `BillingBatchFilterCriteriaNumber`  | 11      |

## externalId Fix — BillingBatchFilterCriteria

`export.json` previously declared `externalId: "JournalEntryRuleName"` for
`BillingBatchFilterCriteria` — a copy-paste artifact from the
`GeneralLedgerJrnlEntryRule` object listed immediately above it.
`JournalEntryRuleName` is not a field on `BillingBatchFilterCriteria` at all.

**Fix:** `externalId` is now `BillingBatchFilterCriteriaNumber`, the object's
auto-number field (`BBFC-000000001` … `BBFC-000000012`), which is unique
across all 11 rows in `BillingBatchFilterCriteria.csv`.

**Portability caveat:** `BillingBatchFilterCriteriaNumber` is an
auto-number field, not a human-authored key. Auto-number values are
assigned sequentially per org and are **not guaranteed to match across
orgs** — a record created in a different order in a fresh org will get a
different number. No other unique direct field exists on this object
(`BatchCriteria.Name` is a lookup traversal, not a direct field, and is
not guaranteed unique per BatchCriteria — see the multiple
`Currency_Iso_code` rows sharing distinct `BatchCriteriaId` parents in the
CSV). Treat this plan as env-specific/reference data rather than a
portable seed until a better direct key is identified upstream.

The SELECT clause also previously included `Id` despite the plan-level
`excludeIdsFromCSVFiles: true` — removed, since raw Salesforce IDs are
non-portable and the field was unused.

## LegalEntity.csv — Reference-Only Artifact

`LegalEntity.csv` (1 record: "Default Legal Entity - US") sits in this
plan's directory but is **not referenced by `export.json`**. LegalEntity is
owned by the `qb-tax` plan (`datasets/sfdmu/qb/en-US/qb-tax/`), which is
responsible for creating/upserting it. This file is left in place as a
local reference/testing artifact only — it is not loaded by this plan and
should not be treated as a second source of truth for LegalEntity data.

## externalId Notes

- `GeneralLedgerAccount.AccountingCode` — direct field, unique per row.
- `GeneralLedgerAcctAsgntRule.Name` — direct field, human-readable.
- `GeneralLedgerJrnlEntryRule.JournalEntryRuleName` — direct field; CSV is
  currently header-only (0 records), so this pass is a no-op until data is
  added.
- `BillingBatchFilterCriteria.BillingBatchFilterCriteriaNumber` — see
  externalId Fix above.

No `$$` composite columns are used in this plan — all externalIds are
single direct fields.

## File Structure

```
qb-accounting/
├── export.json                          # SFDMU data plan (1 pass, 4 objects)
├── README.md                            # This file
├── GeneralLedgerAccount.csv             # 51 records
├── GeneralLedgerAcctAsgntRule.csv       # 8 records
├── GeneralLedgerJrnlEntryRule.csv       # 0 records (header only)
├── BillingBatchFilterCriteria.csv       # 11 records
└── LegalEntity.csv                      # 1 record (reference only — not in export.json; owned by qb-tax)
```
