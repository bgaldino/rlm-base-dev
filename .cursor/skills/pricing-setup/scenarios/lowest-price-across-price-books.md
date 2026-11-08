# Scenario: Lowest Price Across Price Books

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`. Release 264. Sources:
> `ind.pricing_example_calculate_the_lowest_price_of_a_product.htm`,
> `ind.pricing_determine_the_best_price_using_a_pricing_procedure.htm`. Not live-verified.

## Goal

When a product is in several price books, price it at the minimum list price. Help says the engine
looked through all price books and returned the minimum; it gives no figures. [Help]

## Records to set up

| Record | Detail | Owner file |
|---|---|---|
| Laptop in 2+ price books | Entries with different prices, same selling model | [../price-books.md](../price-books.md) |
| Decision table | Price Book Entries V2, active, refreshed | [decision-tables](../../decision-tables/SKILL.md) |
| Recipe mapping | V2 table mapped for List Price | [../pricing-recipes.md](../pricing-recipes.md) |
| Procedure Output Resolution | Name `BestPrice`, element List Price, formula `MIN(ListPrice)`, activated (Price Management > Procedure Output Resolution > New) | [operations-and-troubleshooting.md](../../pricing-procedures/operations-and-troubleshooting.md#4-procedure-output-resolution) |
| Constant | `ResolutionStrategyMinPrice`, Text, default `BestPrice` | [../pricing-actions.md](../pricing-actions.md#constant-resources) |
| Permissions | Design Time user | [../org-enablement-and-permissions.md](../org-enablement-and-permissions.md) |

## Procedure

| # | Element | Key mapping | File |
|---|---|---|---|
| 1 | Pricing Setting | LineItem; price_water_fall, NetUnitPrice, ItemNetTotalPrice | [pricing-setting.md](../../pricing-procedures/elements/pricing-setting.md) |
| 2 | List Price | Price Book Entries V2; Enable Output Resolution; Product, PriceBooks, ProductSellingModel; out ListPrice, Subtotal; Resolution Strategy = `ResolutionStrategyMinPrice`; Use As List = Price Book; Include in Output | [list-price.md](../../pricing-procedures/elements/list-price.md) |

## Expected result

The waterfall shows the smallest list price among the price books that hold Laptop.

## Verify

1. Simulate with Laptop and its selling model.
2. Compare with `sf data query --target-org <sf_alias> -q "SELECT Pricebook2Id, UnitPrice FROM PricebookEntry WHERE Product2Id = '<id>' AND IsActive = true"`; the waterfall price must equal the minimum.
3. With output resolution on, every product needs a matching price book row or that line errors
   (see the output-resolution section linked above).
