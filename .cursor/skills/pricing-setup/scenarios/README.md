# Pricing Scenarios

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`. Release 264. End-to-end walkthroughs from Help;
> setup records are in the sibling files, element detail in `../../pricing-procedures/elements/`.

| Scenario | Goal | Elements | Help source |
|---|---|---|---|
| [simple-pricing-procedure.md](simple-pricing-procedure.md) | List price, volume and manual discount, aggregate for a laptop | Pricing Setting, List Price, Volume Discount, Manual Discount, Aggregate Price | `ind.pricing_simple_pricing_procedure_example.htm` |
| [lowest-price-across-price-books.md](lowest-price-across-price-books.md) | Minimum list price across price books | Pricing Setting, List Price with output resolution | `ind.pricing_example_calculate_the_lowest_price_of_a_product.htm` |
| [sequential-discounts.md](sequential-discounts.md) | Apply tier discounts one after another | Pricing Setting, List Price, Price Adjustment Matrix with output resolution | `ind.pricing_example_apply_discounts_sequentially_for_a_product.htm` |
| [pricing-action-button.md](pricing-action-button.md) | Calculate Price button on an Opportunity | context, procedure, action parameter | `ind.pricing_pricing_action_parameters.htm` |
| [cost-and-margin.md](cost-and-margin.md) | Unit cost, line cost and margin, and a quote total cost | List Price (cost), List Group + Formula-Based Pricing, context mapping, roll-up | Repo wiring (`ind.pricing_define_costs_in_cost_books.htm` calls cost books tracking-only) |
| [full-term-value.md](full-term-value.md) | Full-term value, cost and margin next to the platform's one-period total; a fee on a product subset | List Group + Advanced List Filter + Formula-Based Pricing, context mapping, roll-ups, quote formulas | Custom wiring, measured on a 264 scratch org (no Help example) |

Help `ind.pricing_unique_pricing_scenarios.htm` also lists derived pricing, contract-based pricing,
discount distribution, output resolution, price revisions, promotions and advanced detail line
pricing. Those are covered by element files (`derived-price.md`, `discount-distribution-service.md`,
`promotion-execution.md`, `price-revision.md`), `docs/guides/contract-pricing.md` and
[price-revision-policies.md](../price-revision-policies.md), so they get no scenario file here.
