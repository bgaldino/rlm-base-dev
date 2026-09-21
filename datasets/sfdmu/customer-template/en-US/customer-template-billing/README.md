# customer-template-billing Data Plan

Template SFDMU plan for customer demo billing foundations.

## Scope

This lightweight plan provides demo-oriented billing setup without full QB billing complexity:

- `LegalEntity`
- `PaymentTerm`
- `PaymentTermItem`
- `BillingPolicy`
- `BillingTreatment`
- `BillingTreatmentItem`
- `Product2` billing assignment (`BillingPolicyId` via `BillingPolicy.Name`)

## Design notes

- Uses portable external IDs (name-based, no Salesforce IDs in CSVs).
- Uses `skipExistingRecords: true` on core billing objects to reduce accidental overwrites.
- Avoids multi-pass activation/Apex orchestration by default; keep records demo-safe and extend only when needed.

## Current dataset — Salesforce demo (prefix `SFDC`)

Legal entity `Salesforce, Inc.`; payment term `SFDC Net 30` (Period-Based, 30 Days). The name is
customer-prefixed because the org already carries a generic `Net 30` record, and PaymentTerm
upserts on `Name`.

| BillingPolicy | BillingTreatment | BillingTreatmentItem | Frequency / timing | SKUs |
|---|---|---|---|---|
| `SFDC Annual Advance` | `Salesforce Annual Subscription` | `Salesforce Annual Subscription Item` (`BillingType=Advance`) | Yearly, in advance | `SFDC-MAX-SUITE`, `SFDC-SALES-CORE`, `SFDC-SALES-ADV`, `SFDC-SALES-MAX`, `SFDC-SVC-CORE`, `SFDC-RC-GROWTH`, `SFDC-AF-FLAT`, `SFDC-TABLEAU-NEXT`, `SFDC-SVC-IMPL` |
| `SFDC Monthly Arrears` | `Salesforce Monthly Usage` | `Salesforce Monthly Usage Item` (`BillingType=Arrears`) | Monthly, in arrears | `SFDC-SLACK-BIZPLUS`, `SFDC-USG-FLEX`, `SFDC-USG-CONV` |

`SFDC-BLNG-FLEX` and `SFDC-BLNG-CONV` are usage *definition* products (`billing_required: false`
in the SKU contract) — they are not sellable and intentionally have no `Product2.csv` row.

Yearly/Monthly is carried by the treatment item's `BillingType` plus the record naming; there is
no frequency field on `BillingPolicy`/`BillingTreatment`/`BillingTreatmentItem`. The transactional
`BillingFrequency` lives on the quote/order line.

## Known pitfalls

### BillingPolicy / BillingTreatment / BillingTreatmentItem must start as Draft

Salesforce **rejects creating these objects in `Active` status**. The INSERT fails silently — SFDMU reports "Totally processed 1 records" but the record never appears in the org. Always populate `Status=Draft` in all three CSVs. The qb-billing reference plan uses `Draft` throughout.

Because the records stay in Draft, `Product2.BillingPolicyId` can still be set (the billing assignment does not require the policy to be active). For demos this is sufficient — the verify task only checks that `BillingPolicyId` is non-null. Full activation runs as step 6b of `prepare_customer_demo_catalog` (`activate_customer_demo_billing`, `scripts/apex/activateCustomerDemoBilling.apex`), which promotes BillingTreatmentItem → BillingTreatment → BillingPolicy and sets `DefaultBillingTreatmentId`.

### BillingPolicy must be loaded before the Product2 billing assignment

`export.json` has two object sets. Set 1 loads the billing foundation (`BillingPolicy` before `BillingTreatment` before `BillingTreatmentItem`); set 2 re-reads `BillingPolicy` as `Readonly` and then runs the `Product2` Update. SFDMU caches the `BillingPolicy` ID and resolves the `BillingPolicy.Name` → `BillingPolicyId` lookup on the Product2 step (it materialises the set-2 sources into `source/object-set-2/` automatically from the plan-root CSVs). If the BillingPolicy INSERT failed (e.g. because `Status=Active` was rejected), the cache is empty and every Product2 Update record shows "Same data" (null matches null) — a misleading success log that hides the root failure.

## Usage

1. Populate billing CSVs with customer-specific policy/treatment records.
2. Populate `Product2.csv` to assign a billing policy to each billable SKU.
3. Run after customer PCM load so SKU references resolve.
4. Keep advanced billing lifecycle/activation logic as a separate follow-on enhancement when required.
