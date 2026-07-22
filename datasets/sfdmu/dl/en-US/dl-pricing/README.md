# Delta Term Builder — Pricing dataset

Standard-price-book entries for the **Delta Term Builder** demo catalog. Every
Term-Builder product is **$0** — the demo negotiates *discounts*, not list price,
so each SKU just needs one active `PricebookEntry` at `UnitPrice = 0` on the
Standard Price Book for the Term Annual (1-year `TermDefined`) selling model —
the default for every Term and fare product, so new lines pick up
`BillingFrequency = Annual` / `PeriodBoundary = Anniversary` automatically.

**Load `dl-termbuilder` (PCM) first**, then this plan — the PBEs reference the
products, selling model, and price book those objects establish.

## Model

- One active `PricebookEntry` per Term-Builder SKU (`DL-TERM` + 5 fares +
  5 `DL-TMPL-*` Term Library templates) on the **Standard Price Book**, Term Annual
  (`TermDefined`, 1-year) selling model, `UnitPrice = 0`, currency `USD`. The
  template clones get a $0 PBE so they are well-formed catalog products on par with
  `DL-TERM` (see the sibling `dl-termbuilder` README's Term Library section).
- `Product2` and `Pricebook2` are **Readonly** — the plan reads them only as
  lookup context to resolve the PBE foreign keys; it never creates or modifies
  them (the Standard Price Book is platform-provisioned). `ProductSellingModel`
  is also **Readonly** here — `Term Annual` is provisioned by the sibling
  `dl-termbuilder` plan (loaded first), not by this plan.

## Load order & operations

| # | Object | Operation | External ID | Records |
|---|--------|-----------|-------------|---------|
| 1 | Product2 | Readonly | `StockKeepingUnit` | 11 |
| 2 | ProductSellingModel | Readonly | `Name;SellingModelType` | 1 |
| 3 | Pricebook2 | Readonly | `Name;IsStandard` | 1 |
| 4 | PricebookEntry | Insert | `Product2.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode` | 11 |

`PricebookEntry` uses **`Insert`** (not Upsert): its only logical key is composed
entirely of relationship traversals, which SFDMU v5 cannot match on Upsert
(inserts duplicates every run — Bugs 3 and 5). There is **no `deleteOldData`** —
this plan targets a **clean demo org** with no pre-existing `DL-*` PBEs. If a rerun
is ever needed, first delete the `DL-*` PBEs with a narrowly scoped cleanup keyed on
`Product2.StockKeepingUnit LIKE 'DL-%'`; do **not** add `deleteOldData` (it would
clear the whole PricebookEntry object).

## Files

```
export.json                 # 4-object plan (this dir)
Product2.csv                # 11 records  (Readonly lookup: DL-TERM + 5 fares + 5 templates)
ProductSellingModel.csv     # 1 records  (Readonly lookup: Term Annual)
Pricebook2.csv              # 1 records  (Readonly lookup: Standard Price Book)
PricebookEntry.csv          # 11 records  ($0, USD, Standard, Term Annual)
```

## Run

```bash
# after dl-termbuilder:
sf sfdmu run --sourceusername csvfile --targetusername Delta \
  --path datasets/sfdmu/dl/en-US/dl-pricing
```

## Validation

```bash
python scripts/validate_sfdmu_v5_datasets.py --dataset datasets/sfdmu/dl/en-US/dl-pricing
python scripts/ai/check_plan_readme_consistency.py datasets/sfdmu/dl/en-US/dl-pricing
```
