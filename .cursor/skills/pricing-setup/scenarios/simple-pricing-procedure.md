# Scenario: Simple Pricing Procedure (Laptop)

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`. Release 264. Source:
> `ind.pricing_simple_pricing_procedure_example.htm`. Not live-verified.

## Goal

Price a Laptop (and Printer) with a list price, a volume discount, a discretionary discount and an
aggregate, then check the waterfall in Simulate. Help gives no numeric result. [Help]

## Records to set up

| Record | Detail | Owner file |
|---|---|---|
| Products | Laptop and Printer with attributes and classifications | Help "Create Simple Products" (not in this skill) |
| Price book + entries | Both products as entries | [../price-books.md](../price-books.md) |
| Price adjustment schedule | Volume schedule with tiers for Laptop | [../price-adjustment-schedules.md](../price-adjustment-schedules.md) |
| Selling model | Product Selling Model on entries | [../proration-and-selling-models.md](../proration-and-selling-models.md) |
| Decision tables | Price Book Entries, Volume Discount Entries; active and refreshed | [decision-tables](../../decision-tables/SKILL.md) |
| Recipe mappings | Tables mapped | [../pricing-recipes.md](../pricing-recipes.md) |
| Permissions | Design Time User, Run Time User | [../org-enablement-and-permissions.md](../org-enablement-and-permissions.md) |
| Constant resource | As needed | [../pricing-actions.md](../pricing-actions.md#constant-resources) |

Context Service enabled with a context definition (the example uses SalesTransactionContext).

## Procedure (Name `Laptop Sales`, Usage Type Pricing)

| # | Element | Key mapping | File |
|---|---|---|---|
| 1 | Pricing Setting | in LineItem; out price_water_fall, NetUnitPrice, ItemNetTotalPrice | [pricing-setting.md](../../pricing-procedures/elements/pricing-setting.md) |
| 2 | List Price | table Price Book Entries; Product, PriceBooks, ProductSellingModel; in LineItemQuantity; out ListPrice | [list-price.md](../../pricing-procedures/elements/list-price.md) |
| 3 | Volume Discount | table Volume Discount Entries; schedule id, bounds = LineItemQuantity, product, selling model, effective dates; in Quantity, Input Unit Price = ListPrice | [volume-and-tier-discount.md](../../pricing-procedures/elements/volume-and-tier-discount.md) |
| 4 | Manual Discount | AdjustmentType, AdjustmentValue, Quantity, Input Unit Price = NetUnitPrice | [manual-discount.md](../../pricing-procedures/elements/manual-discount.md) |
| 5 | Aggregate Price | Group By ProductSellingModel; condition LineItemQuantity > 2; SUM(ItemNetTotalPrice) to NetUnitPrice; Include in Output | [aggregate-price.md](../../pricing-procedures/elements/aggregate-price.md) |

Order matters: discounts follow the list price. See
[procedure-anatomy-and-ordering.md](../../pricing-procedures/procedure-anatomy-and-ordering.md).

## Expected result

The waterfall shows the volume and manual discounts applied to the Laptop and Printer lines. Help
gives no figures; compute expected values from your own tiers. [Help]

## Verify

1. Save, click Simulate, enter Laptop inputs, Simulate again
   ([operations-and-troubleshooting.md](../../pricing-procedures/operations-and-troubleshooting.md#2-simulate-and-activate)).
2. No waterfall: refresh decision tables and recheck input values. [Help]
3. Use a test quantity above 2 or the Aggregate condition never fires (inferred).
