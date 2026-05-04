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

## Known pitfalls

### BillingPolicy / BillingTreatment / BillingTreatmentItem must start as Draft

Salesforce **rejects creating these objects in `Active` status**. The INSERT fails silently — SFDMU reports "Totally processed 1 records" but the record never appears in the org. Always populate `Status=Draft` in all three CSVs. The qb-billing reference plan uses `Draft` throughout.

Because the records stay in Draft, `Product2.BillingPolicyId` can still be set (the billing assignment does not require the policy to be active). For demos this is sufficient — the verify task only checks that `BillingPolicyId` is non-null. If full billing activation is required (e.g. for live transaction processing), run a dedicated activation Apex script after loading.

### BillingPolicy lookup from Product2 requires BillingPolicy to be in the same SFDMU object set

The billing `export.json` uses a single object set. `BillingPolicy` is loaded before `Product2` within that set. SFDMU caches the newly inserted `BillingPolicy` ID and resolves the `BillingPolicy.Name` → `BillingPolicyId` lookup when it reaches the `Product2` Update step. If the BillingPolicy INSERT failed (e.g. because `Status=Active` was rejected), the cache is empty and all 13 Product2 Update records show "Same data" (null matches null) — a misleading success log that hides the root failure.

## Usage

1. Populate billing CSVs with customer-specific policy/treatment records.
2. Populate `Product2.csv` to assign a billing policy to each billable SKU.
3. Run after customer PCM load so SKU references resolve.
4. Keep advanced billing lifecycle/activation logic as a separate follow-on enhancement when required.
