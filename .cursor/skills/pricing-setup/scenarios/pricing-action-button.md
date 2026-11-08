# Scenario: Calculate Price Button on an Opportunity

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`. Release 264. Sources: the pricing-action
> articles listed in [../pricing-actions.md](../pricing-actions.md). Not live-verified.

## Goal

Let a user click Calculate Price on an Opportunity and run a chosen procedure. Help gives no numbers.

## Records to set up

| Record | Detail | Owner file |
|---|---|---|
| Extended context definition + Opportunity mapping | Not the base `SalesTransactionContext__stdctx` | [context-service](../../context-service/SKILL.md) |
| Pricing procedure on that context | List Price plus discounts as needed | [procedure-anatomy-and-ordering.md](../../pricing-procedures/procedure-anatomy-and-ordering.md) |
| Price book + entries | Products to price | [../price-books.md](../price-books.md) |
| Permissions | Pricing Admin (parameters), Run Time User (use) | [../org-enablement-and-permissions.md](../org-enablement-and-permissions.md) |
| Pricing action parameter | Object Opportunity, context, mapping, procedure, Effective From | [../pricing-actions.md](../pricing-actions.md#standard-button-quote-order-contract-case-opportunity) |
| Page layout | Calculate Price in the Actions section | same |

## Steps

1. Build and activate the procedure (elements as in [simple-pricing-procedure.md](simple-pricing-procedure.md)).
2. Create the parameter; add the button to the Opportunity layout.
3. Open an Opportunity and click Calculate Price.

## Expected result

Pricing runs through the mapped context and results are stored on the object. [Help]

## Verify

Check the run in the waterfall/logs
([runtime-and-observability.md](../../pricing-procedures/runtime-and-observability.md)); then follow
[Verify in pricing-actions.md](../pricing-actions.md#verify).
