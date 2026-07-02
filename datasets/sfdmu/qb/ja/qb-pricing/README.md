# `qb/ja/qb-pricing` — Japanese localized pricing dataset (NOT YET OPTIMIZED)

> **Status: deferred / work-in-progress.** This `ja` localized pricing set is a
> partial localization of `qb/en-US/qb-pricing` and has **not** been brought up to
> the same SFDMU v5 standard yet. Treat known validation gaps below as **expected and
> deferred** until the localization-optimization work is scheduled — do not file/fix
> them piecemeal. The authoritative, fully-validated set is `qb/en-US/qb-pricing`.

## What has been aligned with en-US

- **CostBook key:** `CostBook` is keyed by single-field `externalId: Name` (matching
  en-US). `CostBook.csv` carries no `$$Name$IsDefault` column, and the parent references
  in `Pricebook2.csv` and `CostBookEntry.csv` use `CostBook.Name` accordingly.

## Known gaps — DEFERRED to the ja-localization-optimization work

These are surfaced by `python scripts/validate_sfdmu_v5_datasets.py` (which reports
`qb/ja/qb-pricing` as FAIL) and are **expected** until the localization pass:

- `PriceAdjustmentTier.csv` — missing the `$$…` composite key column for its
  composite `externalId` (breaks v5 re-import idempotency).
- `PricebookEntry.csv` — missing the `$$Name$Product2.StockKeepingUnit$ProductSellingModel.Name$CurrencyIsoCode`
  composite key column.
- Other rows/values may not yet mirror the en-US dataset's coverage.

When the ja optimization is scheduled, bring this set to full parity with
`qb/en-US/qb-pricing` and remove this notice. Until then, **validate against the
en-US set**; ja failures here are known and tracked.
