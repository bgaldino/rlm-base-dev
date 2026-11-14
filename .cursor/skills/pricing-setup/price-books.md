# Price Books and Price Book Entries

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`. Release 264 / API v68.0. Sources:
> `ind.pricing_price_books_salesforce_pricing.htm`, `ind.pricing_define_prices_in_price_books.htm`,
> `ind.pricing_add_products_as_price_book_entries.htm`, `ind.pricing_create_or_use_predefined_lookup_tables.htm`;
> `datasets/sfdmu/qb/en-US/qb-pricing/README.md`. Not live-verified.

A price book lists products with selling prices; a price book entry (PBE) is one product's list price in
one book, optionally per selling model and currency. The List Price element reads PBEs through the Price
Book Entries decision table, so a PBE only prices a line after that table is refreshed.

## When you need it

- Every org needs at least one price book to price products; a cost book is optional. [Help: `ind.pricing_price_books_salesforce_pricing.htm`]
- Separate books for currencies, regions or customer segments. [Help: `ind.pricing_define_prices_in_price_books.htm`]
- All products in a bundle must be in the same price book as the bundle, or quoting the bundle prices wrongly. [Help]

## Set it up

Permission: Salesforce Pricing Design Time User. [Help]

1. Optional, to link a cost book: Object Manager > Price Book > Page Layouts > Price Book Layout, drag the Cost Book field onto the layout, save. [Help]
2. App Launcher > Price Management > Price Books > New. Name; optional description, validity date range, Active, cost book. Save. [Help]
3. Open the book > Price Book Entries tab > New: product, price book, list price, product selling model (if the product has one). Save. [Help]
4. Refresh the Price Book Entries decision table (see below).

The org ships a predefined Standard Price Book; you can create any number of custom books. [Help] The Help also says you can "create your own standard price book" in Price Management; it does not say how that differs from the predefined one (open question).

## Fields and rules

| UI label | API name | Rules |
|---|---|---|
| Price Book | `Pricebook2` (fields `Name`, `IsStandard`, `IsActive`, `ValidFrom`, `ValidTo`, `CostBookId`) | Validity range and Active are Help-documented; API names from the ERD |
| Price book entry | `PricebookEntry` (`Pricebook2Id`, `Product2Id`, `ProductSellingModelId`, `UnitPrice`, `CurrencyIsoCode` (multicurrency orgs only), `IsActive`, `IsDerived`, `UseStandardPrice`) | `UnitPrice`, product and book are required |
| Product selling model | `ProductSellingModelId` | **Cannot be changed once set on a PBE**; migrating orgs need a support ticket to fix an existing entry [Help] |
| Currency | `CurrencyIsoCode` | One PBE per currency in a multicurrency org [Repo] |
| Derived list price | `IsDerived`, `PricebookEntryDerivedPrice` | `IsDerived` is stored, not computed, and create-only unless the org has the pilot enabled by Salesforce; to clear it, delete and re-insert the entry (not possible while it is a derived or contributing product or has assets; the new entry takes the value you supply). Even with the pilot, an update is blocked by default for a derived product, a contributing product of a derived price, or a product on any asset [Platform behaviour, traced]. Derived product's PBE price must be 0; see [derived-price](../pricing-procedures/elements/derived-price.md) |

For pricing adjustment batch jobs, price adjustment schedules need effective dates and price book entries do not. [Help: `ind.pricing_pricing_adjustment_batch_jobs.htm`] The book itself carries the validity range.

## How pricing uses it

- The [List Price element](../pricing-procedures/elements/list-price.md) looks up the Price Book Entries (V2) decision table with product, price book, selling model and (multicurrency) currency as inputs and writes `ListPrice`. [Help, Repo]
- No matching row means the element leaves earlier values untouched, so a missing PBE shows as an unchanged or zero price, not an error. [Help] Exception: with output resolution enabled on the List Price step, a missing row is a configuration error that stops pricing the line ([output resolution](../pricing-procedures/operations-and-troubleshooting.md#4-procedure-output-resolution)). [Help]
- The decision table must be Active, mapped to the pricing recipe and Fresh. Predefined tables come from the recipe: [create or use predefined lookup tables](../decision-tables/SKILL.md). [Help: `ind.pricing_create_or_use_predefined_lookup_tables.htm`]
- Multicurrency: to add the Currency field to a predefined decision table, deactivate the table, add the field, reactivate. To enable multicurrency with active pricing procedures on predefined tables, deactivate the procedure, enable multicurrency, then reactivate. [Help]
- Refresh and sync rules: [import-export-and-bulk-data.md](./import-export-and-bulk-data.md#after-load-refresh-rule).

## Data and automation

- Objects: `Pricebook2`, `PricebookEntry`, `PricebookEntryDerivedPrice`; cost link via `Pricebook2.CostBookId`. Bulk edits: pricing adjustment batch jobs ([pointer](./import-export-and-bulk-data.md#bulk-price-edits)).
- [Repo] The QuantumBit plan upserts `Pricebook2` and `PricebookEntry` (one row per SKU, selling model and currency, since the repo build is multicurrency; non-USD prices derived from `CurrencyType` rates). `CostBook` loads before `Pricebook2` because of the FK. See `datasets/sfdmu/qb/en-US/qb-pricing/README.md`.

## Verify

```bash
sf data query -q "SELECT Id, Product2.Name, Pricebook2.Name, ProductSellingModel.Name, UnitPrice FROM PricebookEntry WHERE Product2.StockKeepingUnit = '<sku>' AND Pricebook2Id = '<book id>' AND ProductSellingModelId = '<model id>' AND IsActive = true" --target-org <sf_alias>
```

Filter to the price book and selling model you simulate. Add `CurrencyIsoCode` to the SELECT (and a currency filter) only in a multicurrency org; the field does not exist otherwise.

Then confirm the decision table is Fresh ([decision-tables](../decision-tables/SKILL.md)) and run Simulate: the waterfall List Price should equal `UnitPrice`.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Line prices at 0 or stays at earlier value | No PBE for product + book + selling model + currency, or table stale | Query PBE; refresh the table |
| Line errors and stops pricing | Output resolution on and no PBE row for the product | Add the PBE, refresh, or turn off output resolution |
| New PBE ignored | Decision table not refreshed after insert | Refresh/sync |
| Cannot change selling model on a PBE | Platform rule | Create a new PBE; migrated entries need support |
| Bundle components price wrongly | Components in a different book than the bundle | Put all in the same book |
| Wrong-currency price | Currency not an input on the List Price step or table | See list-price Troubleshooting |

## Open questions

- Standard vs custom book behavior in the Price Management app (Help is vague on "create your own standard price book").
- Whether the price book validity range is enforced at pricing time or only at quote selection; Help
  only says it determines validity. The list-price step itself does not test validity dates; it uses
  whatever single row the lookup returns. Don't promise date-based exclusion at pricing time without
  checking the lookup [Platform behaviour, traced].
