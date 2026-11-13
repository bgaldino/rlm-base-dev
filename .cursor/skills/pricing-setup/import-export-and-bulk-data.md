# Pricing Data: View, Export/Import, Sync and Bulk Load

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`. Release 264 / API v68.0. Sources:
> `ind.pricing_view_pricing_data.htm`, `ind.pricing_export_and_import_your_pricing_data.htm`,
> `ind.pricing_considerations_for_importing_and_exporting_pricing_data.htm`, `ind.pricing_sync_pricing_data.htm`,
> `ind.pricing_update_your_product_price_range_entries_decision_table.htm`,
> `ind.pricing_create_or_use_predefined_lookup_tables.htm`, `ind.qocal_set_up_multiple_currencies.htm`,
> `ind.product_catalog_turn_on_list_price_from_cache.htm`; `datasets/sfdmu/qb/en-US/qb-pricing/README.md`. Not live-verified except where tagged [Repo, measured].

How to look at pricing records, move pricing metadata between orgs, and get changed records into the decision
tables pricing reads.

## When you need it

- Records changed (prices, tiers, costs, contracts) and pricing still shows old values: sync/refresh.
- Moving recipes, decision tables, context definitions and procedures to another org: package.
- Loading many price book or adjustment rows: bulk path and its ordering rules.

## View pricing data

Price book entry and price adjustment record pages show a grid by default. To switch to list view: Price Management > open a PBE or adjustment record page > Edit Page > select the Pricing List View component > clear Show Grid View. Needs Experience/Builder rights (member of the site plus Create and Set Up Experiences, or experience admin/publisher/builder). [Help: `ind.pricing_view_pricing_data.htm`]

## Sync pricing data

[Help: `ind.pricing_sync_pricing_data.htm`] Sync refreshes every decision table that is mapped to a pricing recipe **and** has Usage Type = Pricing. Tables with source objects must have Usage Type Pricing for an accurate sync.

[Core] Disagrees with Help on scope: Sync refreshes every **active** decision table mapped to the recipe (the recipe page's Sync) or to any active Revenue Cloud recipe (the Setup button), with no usage-type filter, plus the Derived Pricing Entries and Asset Action Source Entries V2 tables if active. It never activates a table. The button shows for Design Time, Pricing Manager and Pricing Admin users.

[Repo, measured on a fresh 264 build] Sync refreshed all 11 DefaultPricing tables and 2 PricingDiscovery tables (a usage type Help's rule does not name, consistent with core), and no rating, qualification or tax tables ([decision-tables measurement](../decision-tables/lifecycle-and-refresh.md#after-editing-setup-data--what-refreshes-what)). Check Last Refreshed rather than relying on usage type alone.

1. Setup > Quick Find > Salesforce Pricing > Salesforce Pricing Setup.
2. Sync Pricing Data > Sync.

Permissions: Salesforce Pricing Design Time to enable sync; Assetize Order for complete sync of tables. If a complete sync fails, the Help recommends the System Admin permission set. Sync is manual. A scheduled flow can refresh pricing tables on a cadence ([pricing-recipes → Data and automation](pricing-recipes.md#data-and-automation)). After a sandbox refresh or clone, re-run Sync Pricing Data and refresh each table; pricing data does not carry over.

## After-load refresh rule

Any change to source records (`PricebookEntry`, `CostBookEntry`, `PriceAdjustmentTier`, adjustment and condition rows, contract item prices) does not reach pricing until the decision tables that read them are refreshed. After every load or bulk job: run Sync Pricing Data or refresh the specific tables, then confirm Fresh. Mechanics, per-table refresh, staleness checks and CLI tasks: [decision-tables](../decision-tables/SKILL.md) (`lifecycle-and-refresh.md`). Never run verification on an org while refreshes are still queued.

Predefined-table maintenance: adding maximum-price tracking requires editing Product Price Range Entries (deactivate, add result `MaxRecordedPrice`, finish, activate); otherwise the procedure fails once the max setting is on. New orgs can use Product Price Range Entries V2. [Help: `ind.pricing_update_your_product_price_range_entries_decision_table.htm`] See [price-tracking](../pricing-procedures/elements/price-tracking.md).

## Export and import (packaging)

Moves pricing **metadata**: recipes, decision tables, context definitions, pricing procedures. It does not move price book or adjustment records. [Help: `ind.pricing_considerations_for_importing_and_exporting_pricing_data.htm`]

Package steps (Setup > Package Manager > New; add components; Upload; install via the URL, choose admins/all users/profiles). Permission: Salesforce Pricing Design Time. [Help: `ind.pricing_export_and_import_your_pricing_data.htm`]

| Export | Import |
|---|---|
| Export context definitions and decision tables first | Import context definitions and decision tables first |
| Exporting a recipe packages all its mapped decision tables and discovery procedures | Import all recipes and the procedure's decision tables before the pricing procedures |
| The default recipe chosen in Setup ships with the default procedure | |
| Tables tied to a procedure (including the default one) ship with it | |

Before import, check the org's decision table limit; importing without room fails. [Help] Context definitions: [context-service](../context-service/SKILL.md). After install, activate and refresh tables.

## Bulk record loading

- Order parents before children (price book/cost book before entries; schedule before tiers; attribute rule, then conditions, then adjustments with all conditions of a rule in one batch). Details: [price-adjustment-schedules.md](./price-adjustment-schedules.md#data-and-automation).
- Deactivate the schedule before writing tiers or adjustments.
- Multicurrency: one row per currency for each currency-matched record, adjustments included; keep single schedules ([Adding a currency](#adding-a-currency)).
- Finish with the refresh rule above.

## Adding a currency

Prerequisites [Help: `ind.qocal_set_up_multiple_currencies.htm`]: turn on multiple currencies and activate the new currency in Setup; give the currency its prices in a price book; deactivate the pricing procedure version, map the `CurrencyIsoCode` input to `PricingCurrencyCode` in the Pricing Setting element, and activate it again. Enabling multicurrency while procedures on predefined tables are active, or adding the Currency field to a predefined table, needs the procedure or table deactivated first (see [price-books.md → How pricing uses it](price-books.md#how-pricing-uses-it)). With List Price from Cache on, refresh the cache after enabling multicurrency. [Help: `ind.product_catalog_turn_on_list_price_from_cache.htm`]

What a pricing data pack loads for each extra currency, for example EUR next to USD:

| Record | Per currency | Source |
|---|---|---|
| `PricebookEntry` | One row per product, selling model and currency | List Price step passes `CurrencyIsoCode` [Repo: `force-app/main/default/expressionSetDefinition/RLM_DefaultPricingProcedure.expressionSetDefinition-meta.xml`] |
| `CostBookEntry` | One row per product and currency | `RLM_CostBookEntries` has a `CurrencyIsoCode` column [Repo: `unpackaged/pre/5_decisiontables/RLM_CostBookEntries.decisionTable-meta.xml`] |
| `PriceAdjustmentTier` | One row per band and currency, percentage tiers included | The standard adjustment tables match on `PriceAdjustmentScheduleId` and `CurrencyIsoCode`, and the volume, attribute and bundle steps pass `CurrencyIsoCode` [Repo: `datasets/sfdmu/qb/en-US/qb-pricing/README.md`, `RLM_DefaultPricingProcedure`] |
| `BundleBasedAdjustment` | One row per adjustment and currency | Same |
| `AttributeBasedAdjustment` | One row per adjustment and currency | Same. In the repo plan its rules and conditions carry no currency and are shared [Repo] |
| `PriceAdjustmentSchedule` | No: one per type, shared by every currency's children | [price-adjustment-schedules.md → Data and automation](price-adjustment-schedules.md#data-and-automation) |

- Monetary values (`UnitPrice`, `Cost`, `Amount`/`Override` adjustment values) need the currency's own amount; percentage values are copied unchanged, and the repo still loads a row in each currency. [Repo: `scripts/expand_currency_pricing_data.py`] Leaving a currency's row out is a non-match: no adjustment from that adjustment or tier lookup (below).
- [Repo] The QuantumBit plan loads seven currencies (USD corporate, plus GBP, EUR, AUD, CAD, CHF, JPY). The EUR rate lives in `datasets/sfdmu/qb/en-US/qb-pricing/CurrencyType.csv` (`ConversionRate` 0.876364 against USD 1). `scripts/expand_currency_pricing_data.py` builds every non-USD row from the USD row with that rate; it copies tier values unchanged because every QuantumBit tier is a percentage. Refreshing rates: [pricing-wiring → Wrong-currency price returned](../pricing-wiring/SKILL.md#wrong-currency-price-returned-multicurrency-orgs).
- The procedure side must pass `CurrencyIsoCode` on every currency-denominated lookup. Without it, several currency rows give a duplicate-value error (output resolution off), or, on a List Price or Price Tracking step with output resolution on, a resolution pick that can be another currency's row [Platform behaviour, traced, via pricing-wiring]; matrix, Volume and Tier Discount lookups behave differently (same section); a lone other-currency row prices the line [inferred] (same pricing-wiring section).
- Finish with the refresh rule above, then Simulate one line in each currency.

## Bulk price edits

Pricing adjustment batch jobs (list-view/related-list bulk edits of PBEs, tiers and adjustments, 200 records per batch, logs and rerun): see [pricing adjustment batch jobs](../pricing-procedures/runtime-and-observability.md#pricing-adjustment-batch-jobs). Not repeated here.

## [Repo] How this repo loads pricing data

SFDMU plan `datasets/sfdmu/qb/en-US/qb-pricing/` upserts price books, entries, cost books, schedules, tiers and adjustments on externalId keys; reruns do not delete. Plan details: `datasets/sfdmu/qb/en-US/qb-pricing/README.md`; authoring rules: `.cursor/skills/sfdmu-data-plans/SKILL.md`; load then refresh order: `.cursor/skills/pricing-wiring/SKILL.md`.

## Verify

```bash
sf data query -q "SELECT COUNT(Id) FROM PricebookEntry WHERE Pricebook2.Name = '<book>' AND IsActive = true" --target-org <sf_alias>
cci task run check_decision_table_freshness --org <cci_alias>
```

Then Simulate a known product and compare the waterfall with the source row.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Old price after load | Tables not refreshed | Sync / refresh, check Fresh |
| Table skipped by sync | Inactive, or not mapped to the recipe (or to an active Revenue Cloud recipe) [Core] | Activate it and map it |
| Package import fails | Decision table limit, or wrong order | Free space; import contexts and tables first |
| Pricing empty in a cloned sandbox | Data does not carry over | Sync and refresh each table |
| Procedure fails after enabling max price | Range table lacks `MaxRecordedPrice` | Edit table as above |

## Open questions

- Whether Package Manager components include price book records (Help implies metadata only).
- [Platform behaviour, traced] A lookup with no row for the transaction currency returns no match (`CurrencyIsoCode` is a required equals input in the shipped recipe tables). For an adjustment or tier lookup the line gets no adjustment, with no conversion from the corporate currency found; a list-price lookup returns no price. Procedure and lookup path only; no error is raised in the traced path (for a List Price or Price Tracking step with output resolution on, Help says the line stops instead); not measured. Load a row per currency.
- Whether the predefined adjustment tables need the Currency field added by hand when multicurrency is enabled after the procedure exists; Help names only Price Book Entries V2 for that step (`ind.qocal_create_a_pricing_procedure_for_product_discovery.htm`).
- `PricebookEntryDerivedPrice` has `CurrencyIsoCode` (Dev Guide) and the repo plan keys it on currency, but the plan ships no rows, so per-currency derived prices are untested here.
- What Help means by "Only the Place Sales Transaction API supports multi-currency transactions" (`ind.qocal_set_up_multiple_currencies.htm`).
