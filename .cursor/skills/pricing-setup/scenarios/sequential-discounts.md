# Scenario: Sequential Discounts from Price Adjustment Tiers

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`. Release 264. Source:
> `ind.pricing_example_apply_discounts_sequentially_for_a_product.htm`. Not live-verified.

## Goal

Apply several discounts to Laptop in order: the first off the list price, each later one off the
previously discounted price, using `SEQUENCE(TierValue)`.

## Records to set up

| Record | Detail | Owner file |
|---|---|---|
| Price adjustment tiers (schedule `Standard Price Adjustment Tier`; Help activates it, but on 264 inactive tiers still price and an active schedule blocks tier writes [Repo, measured]) | Laptop, One Time, Amount, effective 01-03-2025: 100 (bounds 10-20), 150 (21-40), 200 (41 and up) | [../price-adjustment-schedules.md](../price-adjustment-schedules.md) |
| Custom Advanced decision table (usage Pricing) | Source Price Adjustment Tier; conditions Product2Id = and Name = (AND); results TierValue, AdjustmentType; activate | [decision-tables](../../decision-tables/SKILL.md) |
| Lookup from the tier object to the transaction line | Lets one line link many tiers | [context-service](../../context-service/SKILL.md) |
| Context node, mapping, tags for the tier object | Tag (example `Contributor`) carries the tier name | [context-service](../../context-service/SKILL.md) |
| Recipe mapping | Pricing Recipes > NGPDefaultRecipe > Price Adjustment Matrix > Modify; AdjustmentValue = TierValue, AdjustmentType = AdjustmentType | [../pricing-recipes.md](../pricing-recipes.md) |
| Procedure Output Resolution | `Sequential_Pricing`, element Price Adjustment Matrix, `SEQUENCE(TierValue)`, active | [operations-and-troubleshooting.md](../../pricing-procedures/operations-and-troubleshooting.md#4-procedure-output-resolution) |
| Constant | `ResolutionStrategySequence`, Text, `Sequential_Pricing` | [../pricing-actions.md](../pricing-actions.md#constant-resources) |

Rule [Help]: each attribute value must resolve to one unique decision-table row, and at least one
column must hold unique values for the Use As List tag.

## Procedure

| # | Element | Key mapping | File |
|---|---|---|---|
| 1 | Pricing Setting | LineItem; waterfall, NetUnitPrice, ItemNetTotalPrice | [pricing-setting.md](../../pricing-procedures/elements/pricing-setting.md) |
| 2 | List Price | Price Book Entries V2; out ListPrice | [list-price.md](../../pricing-procedures/elements/list-price.md) |
| 3 | Price Adjustment Matrix | custom table; Enable Output Resolution; Product, Price Adjustment Tier Name = tag `Contributor`; Quantity, Input Unit Price = ListPrice; Strategy `ResolutionStrategySequence`; Use As List = Price Adjustment Tier Name; Include in Output | [price-adjustment-matrix.md](../../pricing-procedures/elements/price-adjustment-matrix.md), [volume-and-tier-discount.md](../../pricing-procedures/elements/volume-and-tier-discount.md) |

## Expected result

Simulate with Product Laptop, Quantity 15, Selling Model One Time, Contributor `Standard Price
Adjustment Tier`. Help states the waterfall shows all associated tier discounts applied
sequentially; it gives no figures. As written, quantity 15 sits only in the 10-20 tier (100), and
Help does not reconcile that with "all discounts"; treat the multi-row outcome as dependent on how
tiers are linked to the line (inferred).

## Verify

1. Simulate as above; read the waterfall for one adjustment per resolved row.
2. On the line's Related tab, confirm several adjustment records link to one line item.
3. Confirm the schedule and the decision table are active and refreshed.
