# Rate Management Domain

15 objects managing rate cards for usage-based pricing, including tiered adjustments and attribute-based rate adjustments.

## Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `RateCard` | Container for rate entries | Name, Type, UsageResourceId |
| `RateCardEntry` | Rate for a product+resource combination | ProductId, RateCardId, UsageResourceId, ProductSellingModelId, RateUnitOfMeasureClassId, RateUnitOfMeasureId |
| `RateAdjustmentByTier` | Tiered adjustment on a rate card entry | RateCardEntryId, ProductId, ProductSellingModelId, RateCardId, LowerBound, UpperBound |
| `RateAdjustmentByAttribute` | Attribute-based adjustment on a rate card entry | RateCardEntryId, RateCardId |
| `PriceBookRateCard` | Junction: PriceBook ↔ RateCard | PriceBookId, RateCardId, RateCardType |
| `RatingFrequencyPolicy` | Controls rating frequency per product/resource | RatingPeriod, ProductId, UsageResourceId |

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
UsageResource ← RateCard (UsageResourceId)
PriceBook2 ← PriceBookRateCard (PriceBookId)
RateCard ← PriceBookRateCard (RateCardId)
BindingObjectCustomExt ← BindingObjectRateCardEntry (BindingObjectId)
```

## Cross-Domain Dependencies

- **From PCM**: Product2, ProductSellingModel, UnitOfMeasure, UnitOfMeasureClass
- **From Usage**: UsageResource, ProductUsageResource (PUR) — rate cards reference the same usage resources as PURs
- **From Pricing**: PriceBook2 — PriceBookRateCard links rate cards to price books

## SFDMU Data Plan: `qb-rates`

5 objects in 1 pass. **Must load after** `qb-rating` (RateCardEntry references UsageResource and PUR).

All junction objects use `Insert` + `deleteOldData: true` due to composite relationship-traversal externalIds.

**Deletion constraint**: `delete_qb_rates_data` must run before `delete_qb_rating_data` — rates FK to PURs.
