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

## Usage

1. Populate billing CSVs with customer-specific policy/treatment records.
2. Populate `Product2.csv` to assign a billing policy to each billable SKU.
3. Run after customer PCM load so SKU references resolve.
4. Keep advanced billing lifecycle/activation logic as a separate follow-on enhancement when required.
