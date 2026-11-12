# Cost Books

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`. Release 264 / API v68.0. Sources:
> `ind.pricing_define_costs_in_cost_books.htm`, `ind.pricing_price_books_salesforce_pricing.htm`;
> `datasets/sfdmu/qb/en-US/qb-pricing/README.md`, `.cursor/skills/pricing-wiring/SKILL.md`. Not live-verified except
> where tagged [Measured] (2026-11-11, a fresh 264 `ent-sb0` scratch org).

A cost book records what a product costs you; each cost book entry is a cost factor stored against a
product record. It is optional and independent of selling price.

## When you need it

- Track internal cost per product for margin analysis. [Help]
- Feed a cost-based List Price step and a margin calculation in a custom or shipped procedure. [Repo]

## Contradiction (Help vs repo)

[Help] states: cost book entries are for tracking only; Salesforce Pricing does not pull them into quote lines,
does not calculate margins or markups from them, and they cannot be referenced directly in pricing procedures.
[Repo] The shipped default procedure runs a [List Price](../pricing-procedures/elements/list-price.md) step on the
Cost Book Entries decision table (output `ItemUnitCost__std`), then a List Group computes cost and margin
(`../pricing-procedures/elements/list-group-and-list-operation.md`). Reading: no out-of-box margin is computed
for you and no direct reference exists, but a decision table over the cost entries, read by List Price, works.
Treat cost-based pricing as custom wiring, not a supported-by-default feature: the default pricing usage type has no cost book element and the pricing runtime reads no cost book entries. [Core]

## Set it up

Permission: Salesforce Pricing Design Time User. [Help]

1. App Launcher > Price Management > Cost Books > New. Name, validity date range, optionally mark as default. Save.
2. From the cost book: Related tab > Cost Book Entry > New. Product (each cost factor is a product record), cost, cost currency, date range, optional description. Save. [Help]
3. Optional: link the book to a price book via the Cost Book field on the price book layout ([price-books.md](./price-books.md#set-it-up)).
4. For pricing to read it: a decision table over `CostBookEntry`, mapped to the pricing recipe, then refreshed (below).

Creating an entry from the cost book record pre-fills the book; from the Cost Book Entry tab you must pick the book. [Help]

## Fields and rules

| UI label | API name | Rules |
|---|---|---|
| Cost Book | `CostBook` (`Name`, `IsDefault`, `EffectiveFrom`, `EffectiveTo`) | Optional default flag [Help, ERD] |
| Cost Book Entry | `CostBookEntry` (`CostBookId`, `ProductId`, `Cost`, `CurrencyIsoCode` (multicurrency orgs only), `EffectiveFrom`, `EffectiveTo`, `Description`) | `Cost` is the cost price |
| Price book link | `Pricebook2.CostBookId` | Load the cost book first when bulk loading [Repo] |

## How pricing uses it

- Not read by default tables; requires a decision table on `CostBookEntry` (shipped `RLM_CostBookEntries`, mapped to `NGPDefaultRecipe` as a recipe table mapping). [Repo: `../pricing-wiring/SKILL.md`]
- The List Price step outputs the cost to a cost variable (`ItemUnitCost__std` in the shipped default procedure), not to `ListPrice`. [Repo]
- The shipped Cost Book Entries table has only two inputs, `ProductId` and `CurrencyIsoCode` [Repo:
  `unpackaged/pre/5_decisiontables/RLM_CostBookEntries.decisionTable-meta.xml`; the cost step
  `Getunitcostfromcostbook` also passes `Quantity`, which the table doesn't read]. [Measured] So the lookup has
  **no book and no date filter**: an entry in a non-default cost book priced, and `EffectiveFrom` and `EffectiveTo`
  don't select the entry.
- So keep one current entry per product and currency across every book the table reads. Retire an old cost by
  editing or deleting its entry, not by closing its date range. To price from one book or by date, add those inputs
  to the table and the step [inferred, not measured].
- The cost is per pricing term; a term line needs the cost formula multiplied by `PricingTermCount`
  ([scenarios/cost-and-margin.md](./scenarios/cost-and-margin.md#term-lines-cost-one-period)).
- Refresh the table after cost changes: [import-export-and-bulk-data.md](./import-export-and-bulk-data.md#after-load-refresh-rule).

## Data and automation

- Objects: `CostBook`, `CostBookEntry`. [Repo] The QuantumBit plan upserts `CostBook` on `Name` and `CostBookEntry` on `CostBook.Name;Product.StockKeepingUnit;CurrencyIsoCode` (the repo build is multicurrency; a single-currency plan drops `CurrencyIsoCode`), one entry per SKU per currency, costs generated below the lowest price. See `datasets/sfdmu/qb/en-US/qb-pricing/README.md`.

## Verify

```bash
sf data query -q "SELECT Id, CostBook.Name, Product.Name, Cost, EffectiveFrom, EffectiveTo FROM CostBookEntry WHERE Product.StockKeepingUnit = '<sku>'" --target-org <sf_alias>
```

The shipped lookup ignores book and dates, so the query spans every book: check that the product has one entry per currency across all of them. Add `CurrencyIsoCode` to the SELECT (and a currency filter) only in a multicurrency org; the field does not exist otherwise.

Simulate with the procedure that has the cost step; the cost variable should equal `Cost`. Check the table is Fresh.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Margin missing or null | No cost entry, or cost table not mapped/refreshed | Query entries; check recipe mapping and freshness |
| Cost appears nowhere on quotes | By design [Help] | Wire a custom procedure step |
| Cost entry has no book | Created from the Cost Book Entry tab | Set the book |
| Line shows an old or another book's cost | More than one entry for the product and currency; the shipped lookup filters on neither book nor date (which entry wins is not measured) | Keep one entry per product and currency; refresh the table |

## Open questions

- Which pricing component type the Cost Book Entries recipe mapping uses in a non-repo org; Help does not describe a predefined cost table.
- Which entry the shipped lookup returns when a product has more than one for the same currency (two books, or an old and a new date range).
