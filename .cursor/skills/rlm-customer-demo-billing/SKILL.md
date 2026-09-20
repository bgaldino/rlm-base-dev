---
name: rlm-customer-demo-billing
description: >-
  Authors the customer-template-billing SFDMU dataset for Revenue Cloud customer demos —
  LegalEntity, PaymentTerm, PaymentTermItem, BillingPolicy, BillingTreatment,
  BillingTreatmentItem, and Product2 billing assignment. Use when building or fixing
  customer demo billing CSVs, Draft vs Active billing status, BillingTreatmentItem
  CurrencyIsoCode errors, or activate_customer_demo_billing ordering.
disable-model-invocation: true
---

# Billing builder

Owns `datasets/sfdmu/customer-template/en-US/customer-template-billing/**`. Authoring only —
never run `cci`, `sf`, or any deploy/import command.

Input: `sku-contract.yaml` (`skus[].billing_required`, `billing_policy_name`, `customer.name`).

## Status must be Draft on create

Salesforce **rejects creating `BillingPolicy`, `BillingTreatment`, and
`BillingTreatmentItem` with `Status = Active`**. The insert fails silently: SFDMU logs
"Totally processed 1 records" and the record never appears.

Set `Status = Draft` in all three CSVs. Activation is a separate step
(`activate_customer_demo_billing`, step 6b) which runs BTI → BT → BP, setting
`DefaultBillingTreatmentId` before activating the policy.

## BillingTreatmentItem.CurrencyIsoCode is read-only

Omit it from both the SFDMU SELECT in `export.json` and the CSV header. Including it makes
the BTI insert fail silently.

## Product2 billing assignment depends on BillingPolicy in the same object set

`Product2.csv` here is an Update that sets `BillingPolicyId` via `BillingPolicy.Name`. The
billing `export.json` uses a single object set, loading `BillingPolicy` before `Product2` so
SFDMU can cache the new policy ID.

Failure signature to recognize: if the `BillingPolicy` insert failed, the cache is empty and
every `Product2` Update row reports **"Same data"** (null matching null) — a misleading
success log that hides the real failure. If you see that, check the BillingPolicy status
first.

## Coverage

Write a `Product2` assignment row for each contract SKU with `billing_required: true`, using
the `billing_policy_name` from the contract. SKUs with `billing_required: false` get no row.

`LegalEntity`, `PaymentTerm`, and `PaymentTermItem` are named from `customer.name` and the
payment terms captured during intake.

## Deletion ordering (context, not your job to run)

The delete script deactivates in reverse order — Policy to Draft plus clear
`DefaultBillingTreatmentId`, Treatment to Draft, TreatmentItem to Draft — before deleting.
Skipping deactivation makes `Database.delete(..., false)` silently leave Active records.

## Conventions

- Portable external IDs only: name-based, never Salesforce IDs in CSVs.
- `skipExistingRecords: true` stays on the core billing objects.
- Keep `;` delimiters in `externalId`; do not convert `Upsert` to `Insert` + `deleteOldData`.

## Before you finish

1. `Status = Draft` in BillingPolicy, BillingTreatment, and BillingTreatmentItem CSVs.
2. No `CurrencyIsoCode` column in the BTI CSV or its SELECT.
3. Every `billing_required: true` SKU has a Product2 row with a policy name that exists in
   `BillingPolicy.csv`.

Deeper detail: `datasets/sfdmu/customer-template/en-US/customer-template-billing/README.md`.
