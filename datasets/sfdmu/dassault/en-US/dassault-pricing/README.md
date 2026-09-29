# dassault-pricing Data Plan

Price books, price book entries and multi-year commitment prices for the
Dassault Systèmes catalog. Generated together with
[`dassault-pcm`](../dassault-pcm/README.md) by
`scripts/dassault/build_dassault_catalog.py`; load `dassault-pcm` first.

```bash
sf sfdmu run --sourceusername CSVFILE --targetusername <username> \
  -p datasets/sfdmu/dassault/en-US/dassault-pricing --canmodify <my-domain host> --noprompt
```

After loading, refresh the `Price_Book_Entry_Decision_Table_v2` and
`Attribute_Based_Adjustment_Decision_Table` decision tables
(`refresh_dt_default_pricing`) so pricing uses the new data.

## Price books

| Workbook Price List | Pricebook2 | Currency |
|---------------------|------------|----------|
| EuroZone Price List | EuroZone Price List | EUR |
| USA Price List | USA Price List | USD |

Each price also gets a Standard Price Book entry in the same currency, which
Salesforce requires before a custom price book entry can exist.

## Multi-year commitment prices

TBL2, TBL3 and TSC3 have no selling model of their own (Salesforce allows one
selling model per type/term/unit and a term of 1 for Annual). They are priced
as attribute-based **Override** adjustments on the yearly `Term Annual` price,
driven by the `Commitment` attribute from `dassault-pcm`:

| Commitment | Products | Yearly price applied |
|------------|----------|----------------------|
| 1 Year | all | YLC / YSC (price book entry, no adjustment) |
| 2 Years | on premise | TBL2 ÷ 2 |
| 3 Years | on premise | TBL3 ÷ 3 |
| 3 Years | public cloud | TSC3 |

**Assumption:** TBL2 / TBL3 are read as the total for the whole term and TSC3
as a yearly price, because TBL2 and TBL3 exceed the yearly YLC price while TSC3
is below YSC. Change `COMMITMENT_PRICES` in the generator if this is wrong. The
commitment does not set the quote's subscription term; the rep sets both.

Each price book has its own `Attribute` schedule:
`DS EuroZone Attribute Based Adjustment` (EUR) and
`DS USA Attribute Based Adjustment` (USD). There is one rule per product and
commitment (`DS <SKU> Commitment <n> Years`) with one `equals` condition, and
one adjustment per rule and currency.

## Passes (`useSeparatedCSVFiles`)

| Pass | CSV folder | Loads |
|------|------------|-------|
| 1 | plan root | `Pricebook2`, Standard Price Book entries (276), adjustment schedules (2), rules (62), conditions (62), adjustments (124) |
| 2 | `objectset_source/object-set-2/` | EuroZone / USA entries (276) |

`ProductSellingModel`, `Product2` and `AttributeDefinition` are `Readonly`.

## Objects

| Pass | Object | Operation | External ID |
|------|--------|-----------|-------------|
| 1, 2 | ProductSellingModel | Readonly | `Name` |
| 1, 2 | Product2 | Readonly | `StockKeepingUnit` |
| 1 | Pricebook2 | Upsert | `Name` |
| 2 | Pricebook2 | Readonly | `Name` |
| 1, 2 | PricebookEntry | Upsert | `Pricebook2.Name;Product2.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode` |
| 1 | AttributeDefinition | Readonly | `Code` |
| 1 | PriceAdjustmentSchedule | Upsert | `Name` |
| 1 | AttributeBasedAdjRule | Upsert | `Name` |
| 1 | AttributeAdjustmentCondition | Upsert | `AttributeBasedAdjRule.Name;AttributeDefinition.Code;Product.StockKeepingUnit` |
| 1 | AttributeBasedAdjustment | Upsert | `AttributeBasedAdjRule.Name;PriceAdjustmentSchedule.Name;Product.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode` |

`Pricebook2.Name` is part of the entry key because the same product, selling
model and currency exist in both the Standard and the custom price book.

## Idempotency

Upsert only; nothing is deleted. A second run reported no inserts and the org
has no duplicate entries per price book, product, selling model and currency.
