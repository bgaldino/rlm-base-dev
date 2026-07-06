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

`PriceAdjustmentTier.csv` and `PricebookEntry.csv` now carry the `$$…`
composite key columns matching their declared `externalId`s (this gap is
resolved — do not re-flag it). Two real divergences from `qb/en-US/qb-pricing`
remain, both intentional per `export.json`:

- **`PricebookEntryDerivedPrice` is `excluded: true`** in this plan (en-US
  loads it via `Insert`). Derived pricing is not yet localized for ja.
- **`PriceAdjustmentTier` has `skipExistingRecords: true`** in this plan
  (en-US does not set this flag). Re-runs will not overwrite existing tier
  records in ja orgs.
- Other rows/values may not yet mirror the en-US dataset's coverage.

When the ja optimization is scheduled, bring this set to full parity with
`qb/en-US/qb-pricing` (in particular, un-exclude `PricebookEntryDerivedPrice`
once derived pricing is localized) and remove this notice. Until then,
**validate against the en-US set**; the two divergences above are known and
tracked.
