# q3-pricing Data Plan

> **Shared records follow qb (todo 325).** Where q3 and qb load the same reference record, q3 uses qb's key and values, so the two shapes layer into one org: qb's selling-model names, its schedule dates for the three shared schedules, and the 'Standard Cost Book' on the standard price book. Records qb doesn't have stay q3's own. Currency rates stay q3's: its prices in each currency follow them, so they move together (todo 328). An org loaded with q3 before todo 325 has the old selling models, units and classes; a reload adds the renamed ones beside them (and their entries, options and rate card entries), so rebuild it rather than reload it.

SFDMU data plan for Q3 pricing: currency types, price books and entries, price adjustment schedules and tiers, attribute- and bundle-based adjustments, derived prices and cost books. It loads in `prepare_pricing_data` when `q3` is on and `qb` is off, through `insert_q3_pricing_data`.

> **Reload-safe (todo 319, the qb-pricing pattern from todo 298).** Every object matches on its externalId and nothing is deleted before a load. The seven objects that used to load as `Insert` after `delete_q3_pricing_data` (PriceAdjustmentTier, AttributeAdjustmentCondition, AttributeBasedAdjustment, BundleBasedAdjustment, PricebookEntry, PricebookEntryDerivedPrice, CostBookEntry) are `Upsert` on the same keys, with their traversal key fields in each SELECT (owner-approved, 2026-11-02).

## Currencies

- **Eleven currencies, USD corporate.** CHF was added in todo 210, so qb-tax's Swiss legal entity loads on a q3 build. Its 74 entries mirror the EUR rows at 0.89× the USD price, the same Dec-2024-era basis as the other q3 ratios.
- **`ConversionRate` is foreign units per 1 USD**, and equals the ratio the q3 prices use (EUR 0.96, JPY 149.22, …). Before todo 210 the file carried the inverse for every currency except USD (e.g. JPY 0.0067), which skewed converted amounts in roll-ups and reports but not price-book prices. A reload updates the rates in place (`CurrencyType` is `Upsert` on `IsoCode`).
- **q3-rates has no currency column**, so its rate card entries load in the corporate currency only; CHF rates were not added.

## Two passes

- **Pass 1** loads everything except the custom price book's entries.
- **Pass 2** loads the Nonprofit book's `PricebookEntry` rows. The platform rejects a custom-book entry whose Standard entry doesn't exist yet (`STANDARD_PRICE_NOT_DEFINED`), and when both load in one batch it doesn't exist. On a fresh 264 q3 build all 60 Nonprofit rows were rejected.

Both passes read the root `PricebookEntry.csv`. Each pass's `sourceRecordsFilter` picks its book's rows from the CSV, and its `WHERE Pricebook2.IsStandard = …` scopes the target query; SFDMU applies a WHERE to the target only, never to CSV rows. Pass 2 declares Product2, ProductSellingModel and Pricebook2 `Readonly` so the entry lookups resolve.

## Keys that differ from qb-pricing

- **`PricebookEntry`** keys on `Pricebook2.Name;Product2.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode`. The same SKU, selling model and currency is in both books, so without the book part an Upsert can match the other book's entry (measured on qb-pricing, todo 298). `PricebookEntryDerivedPrice`'s `PricebookEntry.$$…` reference carries the book too. Both objects are listed in `$ownSchemaObjects` in `export.json`, so post-processing keeps their own columns when it aligns an extraction to qb-pricing, whose headers have no book part.
- **`PriceAdjustmentSchedule`** is `Upsert` on `Name`, like qb-pricing; it was `Update` on `Name;CurrencyIsoCode`. A 264 org seeds only the Attribute, Bundle and Price Adjustment Tier schedules, so "Standard Tier Based Adjustment" and "Standard Volume Based Adjustment" are created here. The children reference the schedule by `PriceAdjustmentSchedule.Name`.

## Price adjustment schedules and tiers

- **The five tiers hang off "Standard Price Adjustment Tier"**, the one volume schedule `RLM_DefaultPricingProcedure` reads (`__VOLUMEPasID__`), as in qb-pricing. The source org put them on "Standard Tier Based Adjustment" (HDS001) and "Standard Volume Based Adjustment" (MO001), which no procedure step reads, so they never priced. That was measured on a fresh 264 q3 build, with those schedules active or inactive (todo 319). Their `EffectiveFrom` is 2024-03-26, on or after the schedule's start (qb's 2023-01-01 since todo 325), since the platform rejects a tier dated before its schedule. HDS001's source schedule was Slab; on this Range schedule its whole quantity takes the tier's rate. An org loaded before todo 319 keeps its 5 old tiers on the Tier/Volume Based schedules. They never price and a reload ignores them, but an extraction from that org pulls them back into the CSV, so drop them from it. Delete them by hand (with their schedule inactive), or run `delete_q3_pricing_data` (all tiers, org-wide) and reload.
- **Measured on a fresh 264 q3 build** (Place Sales Transaction, USD, One-Time):
  - HDS001 (list 49.99): 44.99 at qty 7 and 42.49 at qty 12. Its top tier ends at 15, so qty 17 is undiscounted, as in the source org.
  - MO001 (list 144.99): 130.49 at qty 7, 123.24 at qty 12 and 115.99 at qty 17.
- **All three volume schedules load `IsActive=false`.** The platform rejects any `PriceAdjustmentTier` insert, update or delete while its schedule is active (#656), and the tiers price with it inactive. The Tier/Volume Based schedules hold no tiers now; they are kept as the source org has them.
- **Removed:** two tiers on the contract schedule "PAS For Contract #00000102" (MO001, 25% and 30%). The plan loads only `WHERE ContractId = NULL` schedules and creates no Contract (owner, 2026-11-02).

## Removed rows

`PricebookEntryDerivedPrice` lost its SLKSRC001 row. It had no `Product`, `ProductSellingModel` or `PricebookEntry`, only a contributing product, and the platform rejected it ("Specify valid input details"). The source org's matching entry no longer exists.

## Teardown

`delete_q3_pricing_data` deletes every record of the seven objects above, org-wide, children first. Use it only for a manual full teardown; `prepare_pricing_data` reloads in place.

<!-- generate_plan_readme:begin -->
<!-- Generated by scripts/ai/generate_plan_readme.py from export.json + CSVs.
     Regenerate with the same command after changing this plan's objects,
     operations, or externalIds rather than hand-editing this block — content
     outside these markers (narrative sections) is preserved on regeneration. -->

## Objects

| # | Object | Pass | Operation | External ID | Records |
|---|--------|------|-----------|-------------|---------|
| 1 | CurrencyType | 1 | Upsert | IsoCode | 11 |
| 2 | ProrationPolicy | 1 | Update | Name | 1 |
| 3 | ProductSellingModel | 1 | Readonly | Name;SellingModelType | — |
| 4 | ProductSellingModel | 2 | Readonly | Name;SellingModelType | — |
| 5 | AttributeDefinition | 1 | Readonly | Code | — |
| 6 | Product2 | 1 | Readonly | StockKeepingUnit | — |
| 7 | Product2 | 2 | Readonly | StockKeepingUnit | — |
| 8 | CostBook | 1 | Upsert | Name | 1 |
| 9 | CostBook | 2 | Readonly | Name | — |
| 10 | Pricebook2 | 1 | Upsert | Name;IsStandard | 2 |
| 11 | Pricebook2 | 2 | Readonly | Name;IsStandard | — |
| 12 | PriceAdjustmentSchedule | 1 | Upsert | Name | 5 |
| 13 | PriceAdjustmentTier | 1 | Upsert | PriceAdjustmentSchedule.Name;Product2.StockKeepingUnit;ProductSellingModel.Name;ProductSellingModel.SellingModelType;TierType;TierValue;LowerBound;CurrencyIsoCode;EffectiveFrom | 5 |
| 14 | AttributeBasedAdjRule | 1 | Upsert | Name | 13 |
| 15 | AttributeAdjustmentCondition | 1 | Upsert | AttributeBasedAdjRule.Name;AttributeDefinition.Code;Product.StockKeepingUnit | 14 |
| 16 | AttributeBasedAdjustment | 1 | Upsert | AttributeBasedAdjRule.Name;PriceAdjustmentSchedule.Name;Product.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode | 5 |
| 17 | BundleBasedAdjustment | 1 | Upsert | PriceAdjustmentSchedule.Name;Product.StockKeepingUnit;ParentProduct.StockKeepingUnit;RootBundle.StockKeepingUnit;ProductSellingModel.Name;ParentProductSellingModel.Name;RootProductSellingModel.Name;CurrencyIsoCode | 4 |
| 18 | PricebookEntry | 1 | Upsert | Pricebook2.Name;Product2.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode | 820 |
| 19 | PricebookEntry | 2 | Upsert | Pricebook2.Name;Product2.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode | 820 |
| 20 | PricebookEntryDerivedPrice | 1 | Upsert | Pricebook.Name;PricebookEntry.Product2.StockKeepingUnit;PricebookEntry.ProductSellingModel.Name;Product.StockKeepingUnit;ContributingProduct.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode | 5 |
| 21 | CostBookEntry | 1 | Upsert | CostBook.Name;Product.StockKeepingUnit;CurrencyIsoCode | 0 |

## Required source CSVs

<!-- Only CSVs a live-writable declaration must load. A source-free declaration's CSV
     is not required and is omitted here even if one ships: a Readonly/Delete object
     resolves from the target org, and an excluded object is skipped entirely before
     load. -->

```
CurrencyType.csv                         # 11 records
ProrationPolicy.csv                      # 1 record
CostBook.csv                             # 1 record
Pricebook2.csv                           # 2 records
PriceAdjustmentSchedule.csv              # 5 records
PriceAdjustmentTier.csv                  # 5 records
AttributeBasedAdjRule.csv                # 13 records
AttributeAdjustmentCondition.csv         # 14 records
AttributeBasedAdjustment.csv             # 5 records
BundleBasedAdjustment.csv                # 4 records
PricebookEntry.csv                       # 820 records
PricebookEntryDerivedPrice.csv           # 5 records
CostBookEntry.csv                        # 0 records
```
<!-- generate_plan_readme:end -->
