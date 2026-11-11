# Rate Management Domain

11 objects managing rate cards for usage-based pricing, including tiered adjustments and attribute-based rate adjustments.

## Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `RateCard` | Container for rate entries | Name, Type, EffectiveFrom, EffectiveTo (no usage-resource lookup: the resource is on each `RateCardEntry`) |
| `RateCardEntry` | Rate for a product+resource combination | ProductId, RateCardId, UsageResourceId, ProductSellingModelId, RateUnitOfMeasureClassId, RateUnitOfMeasureId |
| `RateAdjustmentByTier` | Tiered adjustment on a rate card entry | RateCardEntryId, ProductId, ProductSellingModelId, RateCardId, LowerBound, UpperBound |
| `RateAdjustmentByAttribute` | Attribute-based adjustment on a rate card entry | RateCardEntryId, RateCardId |
| `PriceBookRateCard` | Junction: PriceBook ↔ RateCard | PriceBookId, RateCardId, RateCardType |
| `RatingFrequencyPolicy` | Controls rating frequency | RatingPeriod, RatingDelayDuration, RatingDelayDurationUnit — `ProductId` and `UsageResourceId` were **removed in 264**; bind it to a product and resource through `ProductUsageResourcePolicy.RatingFrequencyPolicyId` (see `usage.md`) |

## Supporting Objects

| Object | Purpose |
|--------|---------|
| `RatingRequest` | Runtime rating request record |
| `RatingRequestBatchJob` | Batch rating job |
| `BindingObjectRateCardEntry` | Binding object for rate card entries |
| `BindingObjectRateAdjustment` | Binding object for rate adjustments |
| `BindingObjectCustomExt` | Custom extension for binding objects |

## Key Relationships

```
RateCard ← RateCardEntry (RateCardId)
RateCard ← RateAdjustmentByTier (RateCardId)
RateCard ← RateAdjustmentByAttribute (RateCardId)
RateCardEntry ← RateAdjustmentByAttribute (RateCardEntryId)
Product2 ← RateCardEntry (ProductId)
ProductSellingModel ← RateCardEntry (ProductSellingModelId)
UsageResource ← RateCardEntry (UsageResourceId)
RatingFrequencyPolicy ← ProductUsageResourcePolicy (RatingFrequencyPolicyId, Usage domain)
PriceBook2 ← PriceBookRateCard (PriceBookId)
RateCard ← PriceBookRateCard (RateCardId)
BindingObjectCustomExt ← BindingObjectRateCardEntry (BindingObjectId)
```

## Cross-Domain Dependencies

- **From PCM**: Product2, ProductSellingModel, UnitOfMeasure, UnitOfMeasureClass
- **From Usage**: UsageResource, ProductUsageResource (PUR) — rate cards reference the same usage resources as PURs
- **From Pricing**: PriceBook2 — PriceBookRateCard links rate cards to price books

## SFDMU Data Plan: `qb-rates`

5 objects in 2 passes. **Must load after** `qb-rating` (RateCardEntry references UsageResource, which `qb-rating` loads).

Nothing is deleted (todo 298). Every object is `Upsert` on its composite relationship-traversal externalId.
- **RateCardEntry, pass 1:** `skipExistingRecords`, so a missing entry is inserted as Draft (RateAdjustmentByTier requires a Draft parent).
- **RateCardEntry, pass 2:** `Update` without Status.
- **Activation:** `activate_rates`.
- **Platform locks:** an Active RateCardEntry accepts only Status changes, and a RateAdjustmentByTier under an Active entry can't be edited.

**Deletion constraint** (manual full teardown only): `delete_qb_rates_data` must run before `delete_qb_rating_data` — rates FK to PURs.
