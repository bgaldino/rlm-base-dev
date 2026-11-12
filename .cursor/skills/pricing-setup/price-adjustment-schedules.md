# Price Adjustment Schedules and Adjustment Records

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`. Release 264 / API v68.0. Sources:
> `ind.pricing_price_adjustment_schedules_salesforce_pricing.htm`, `ind.pricing_create_price_adjustment_schedules.htm`,
> `ind.pricing_create_price_adjustment_tiers_volume_discounts.htm`, `ind.pricing_create_attribute_based_adjustments.htm`,
> `ind.pricing_create_bundle_based_adjustments.htm`, `ind.pricing_define_price_impacting_attributes.htm`,
> `ind.pricing_attribute_based_pricing_limits.htm`, `ind.pricing_considerations_for_migrating_attribute_based_adjustments.htm`;
> `datasets/sfdmu/qb/en-US/qb-pricing/README.md`. Not live-verified.

A price adjustment schedule is the container; tier, attribute-based and bundle-based adjustment records hang
off it and hold the discount rows. The Volume/Tier, Attribute Based and Bundle Based pricing elements read them
through decision tables. This file covers the records; Builder fields are in the element files.

## When you need it

| Need | Schedule type | Child records | Procedure side |
|---|---|---|---|
| Discount by quantity | Volume | `PriceAdjustmentTier` | [volume-and-tier-discount](../pricing-procedures/elements/volume-and-tier-discount.md) |
| Discount by product attributes | Attribute | `AttributeBasedAdjRule`, `AttributeAdjustmentCondition`, `AttributeBasedAdjustment` | [attribute-based-price](../pricing-procedures/elements/attribute-based-price.md) |
| Discount for products sold in a bundle | Bundle | `BundleBasedAdjustment` | [bundle-based-price](../pricing-procedures/elements/bundle-based-price.md) |

## Set it up

Permission: Salesforce Pricing Design Time; Salesforce Pricing Manager for the Attribute Adjustment Condition object. [Help]

Prerequisites: a product selling model and products in a price book. [Help]

1. Use a predefined schedule (Standard Price Adjustment Tier, Standard Attribute Based Adjustment, Standard Bundle Based Adjustment) or create one: App Launcher > Price Adjustment Schedules > New. Name; Adjustment Method (Range or Slab); Schedule Type (Volume, Attribute, Bundle); Effective From (and optional Effective To; blank means indefinite). Existing schedules can be cloned. [Help]
2. **Deactivate** the schedule before adding records to it. [Help] On 264 any tier write fails while the schedule is active, and tiers on an inactive schedule still price, so this repo leaves "Standard Price Adjustment Tier" inactive. [Repo, measured]
3. Add child records (below). Direct launch from the App Launcher also works, then pick the schedule.
4. Open the schedule and select Active (Help). For volume tiers on 264 this is not needed for pricing and blocks later tier writes (step 2).
5. Refresh the adjustment decision tables ([refresh rule](./import-export-and-bulk-data.md#after-load-refresh-rule)).

Editing: updating price details creates another record rather than editing in place (Help; wording partly lost in the snapshot). [Help]

### Tiers (Volume)

Product, product selling model, schedule (type Volume; no standalone tiers), tier type, tier value, lower and upper bound, effective dates. [Help]

- Bounds are inclusive and tiers cannot overlap; tiers sharing an effective date must be consecutive with no gaps.
- For a unique Product + Selling Model + Schedule + Currency + Effective Dates, quantity ranges must not overlap; avoid duplicates, especially with multicurrency off.
- [Repo] The platform rejects insert/update/delete of a tier while its schedule is active. [Platform behaviour, traced] This is write-time validation only (inserting, deleting or undeleting tiers, editing bounds); the procedure-path tier lookup has no active input, so an inactive tier row still prices there (a separate store-pricing path does filter on active). Delete or exclude tiers you do not want priced.

### Attribute-based

1. Make the attribute price-impacting: Price Management > Products > product > Related > Overridden Inherited Attributes > attribute (use Configure on the inherited attribute first if needed) > edit Product Attribute Definition > Is Price Impacting. The attribute must be active. [Help: `ind.pricing_define_price_impacting_attributes.htm`]
2. On the Attribute Based Adjustment schedule: product, selling model, adjustment type, adjustment value, effective dates, Next, then conditions (attribute, operator, value). Save.

### Bundle-based

Root bundle and its selling model, parent product and its selling model, product and its selling model, adjustment type and value, effective dates, schedule. All products must be in the price book. [Help]

## Fields and rules

| UI label | API name | Rules |
|---|---|---|
| Adjustment Method | `PriceAdjustmentSchedule.AdjustmentMethod` | Range: same discount options for all; Slab: different discount per band [Help] |
| Schedule Type | `PriceAdjustmentSchedule.ScheduleType` | Volume / Attribute / Bundle |
| Effective From / To | `EffectiveFrom`, `EffectiveTo` | Blank To means no end |
| Active | `PriceAdjustmentSchedule.IsActive` | Deactivate before adding records |
| Tier type | `PriceAdjustmentTier.TierType` | `AdjustmentPercentage` (Percentage), `AdjustmentAmount` (Amount), `OverrideAmount` (Override) (ERD) |
| Tier value / bounds | `TierValue`, `LowerBound`, `UpperBound` | Positive integer lower bound (ERD) |
| Adjustment type / value | `AttributeBasedAdjustment`/`BundleBasedAdjustment` `.AdjustmentType`, `.AdjustmentValue` | Percentage, Amount, Override |
| Rule / condition | `AttributeBasedAdjRule`, `AttributeAdjustmentCondition` (`AttributeDefinitionId`, `Operator`, typed value fields) | Conditions belong to a rule |
| Conditions hash | `AttributeBasedAdjustment.AttributeAdjConditionsHash` | Regenerated when a condition is saved [Help] |
| Currency | `CurrencyIsoCode` on each child (multicurrency orgs only) | See Data and automation |

### Attribute limits [Help: `ind.pricing_attribute_based_pricing_limits.htm`]

- Numeric (Number, Currency, Percentage) and number-picklist values are stored with a decimal: enter `10.0`, not `10`, or the adjustment will not match.
- Picklist with Boolean data type is unsupported (design-time error); use a Checkbox/Boolean attribute.
- Use only attributes that belong directly to the selected product classification; inherited ones can show in the UI but fail validation on save.
- Attributes with an overridden bundle context are unsupported; define the attribute once.

## How pricing uses it

Each element resolves the schedule and matches child rows via a decision table (standard adjustment tables match on schedule id and currency [Repo]). Procedure parameters, ordering and discount math: the three element files above. Record data is only visible to pricing after the tables are refreshed.

## Data and automation

- Bulk edits to tiers, adjustments and entries: pricing adjustment batch jobs ([pointer](./import-export-and-bulk-data.md#bulk-price-edits)).
- **Migration order** (Data Loader/API) [Help: `ind.pricing_considerations_for_migrating_attribute_based_adjustments.htm`]: Attribute Based Adjustment Rules, then Attribute Adjustment Conditions, then Attribute Based Adjustments. Load all conditions of one rule in a single batch; never split them across parallel batches (hash conflicts block application). No bulk validator exists; check in the Pricing Operations Console.
- [Repo] One schedule per type (USD), shared by all currencies' children, which are told apart by their own `CurrencyIsoCode` (the repo build is multicurrency); do not create per-currency schedules. The plan upserts the Tier schedule with `IsActive=false` so tiers can reload. See `datasets/sfdmu/qb/en-US/qb-pricing/README.md`.

## Verify

```bash
sf data query -q "SELECT Id, Name, ScheduleType, AdjustmentMethod, IsActive, EffectiveFrom, EffectiveTo FROM PriceAdjustmentSchedule" --target-org <sf_alias>
sf data query -q "SELECT Product2.Name, ProductSellingModel.Name, TierType, TierValue, LowerBound, UpperBound, EffectiveFrom, EffectiveTo FROM PriceAdjustmentTier WHERE PriceAdjustmentScheduleId = '<id>' AND Product2Id = '<product id>' AND ProductSellingModelId = '<model id>' ORDER BY LowerBound" --target-org <sf_alias>
```

Keep only tiers whose effective dates cover the pricing date. Add `CurrencyIsoCode` to the SELECT (and a currency filter) only in a multicurrency org; the field does not exist otherwise.

Simulate a line at a quantity inside a band and check the waterfall step.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Cannot add or change tiers | Schedule is active | Deactivate, edit, refresh (reactivating is not needed for volume tiers on 264; step 4) |
| Tier discount missing for non-USD | Schedule duplicated per currency, or currency not matched. A missing child row in that currency is a non-match, so no adjustment [Platform behaviour, traced; not measured] ([open question](./import-export-and-bulk-data.md#open-questions)) | Single schedule; load one child row per currency ([Adding a currency](./import-export-and-bulk-data.md#adding-a-currency)) |
| Attribute discount not applied (numeric) | Value without `.0` | Use `10.0` |
| Attribute discount not applied after migration, table fresh | Conditions hash mismatch | Save an affected condition unchanged, then run a validation transaction |
| Save error on attribute selection | Inherited or Boolean-picklist attribute | See limits |
| No adjustment | Outside effective dates, or table stale. An inactive schedule does not stop volume tiers on 264 [Repo, measured] | Check dates and freshness |

## Open questions

- Exact meaning of the Range vs Slab methods in the tables; Help gives examples only.
