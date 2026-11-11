# Scenario: Cost and Margin on Quote Lines

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`, indexed in [README.md](README.md).
> Release 264. Unlike the other scenarios this one has no single Help example, because Help
> calls cost books tracking-only. It assembles the repo's shipped wiring end to end. Sources
> are tagged `[Help]`, `[Repo: <path>]` and `[inferred]`.

**Goal:** every quote line shows unit cost, total cost, margin % and margin amount, and the
quote shows a total cost. A source's costs (standard costs, loaded labour rates) become
cost book entries.

## Wiring, in order

| # | Layer | What | Where it's documented |
|---|---|---|---|
| 1 | Data | `CostBook` + one `CostBookEntry` per product (and currency), with `Cost`, `EffectiveFrom` and `EffectiveTo`. The QuantumBit plan loads 623 entries (Upsert on `CostBook.Name;Product.StockKeepingUnit;CurrencyIsoCode`) [Repo: `datasets/sfdmu/qb/en-US/qb-pricing/`] | [../cost-books.md](../cost-books.md) |
| 2 | Lookup | Decision table `RLM_CostBookEntries` over `CostBookEntry`, mapped to `NGPDefaultRecipe`, then refreshed after every cost change | `../../decision-tables/authoring-and-data-model.md`, `../../pricing-wiring/SKILL.md` |
| 3 | Unit cost | List Price step `Getunitcostfromcostbook` (top level, seq 6) writes the cost to `ItemUnitCost__std`, not to `ListPrice` [Repo: `force-app/main/default/expressionSetDefinition/RLM_DefaultPricingProcedure.expressionSetDefinition-meta.xml`] | `../../pricing-procedures/elements/list-price.md` |
| 4 | Line cost and margin | List Group `Calculatecostandmarginforpricedlines` filters lines with `ItemUnitCost__std` not null. The formula step under it writes `ItemTotalCost__std = ItemUnitCost__std * LineItemQuantity`, `ItemMargin__std = (ItemNetTotalPrice - total cost) / ItemNetTotalPrice` and `ItemMarginAmount__std` | `../../pricing-procedures/elements/formula-based-pricing.md`, `../../pricing-procedures/elements/list-group-and-list-operation.md` |
| 5 | Persisted fields | `RLM_SalesTransactionContext` maps those tags to `QuoteLineItem.UnitCost`, `TotalCost`, `Margin` and `MarginAmount` (and the same on order products) [Repo: `docs/references/context-definitions/RLM_SalesTransactionContext.contextDefinition-meta.xml`] | `../../context-service/SKILL.md` |
| 6 | Quote total | No shipped aggregate sums cost or margin onto the quote. Use a roll-up summary field on `QuoteLineItem.TotalCost`, as the manufacturing bundle does with `Quote.RLM_MFG_Total_Cost__c` [Repo: `unpackaged/post_manufacturing_core/objects/Quote/fields/`]. Derive quote margin from it and the quote total | `../../pricing-procedures/procedure-anatomy-and-ordering.md` (why a formula after the DDS tail is rejected or lags) |
| 7 | Visibility | Add the line fields to the line editor's Display Columns. Restrict unit cost to the users who may see it with field-level security | Help `ind.qocal_select_fields_for_the_line_editor.htm`, `../../apex-security-hardening/SKILL.md` (permission sets) |

## Modeling costs from a source

- **One entry per product and currency.** A cost that varies by configuration needs a
  product per variant, or a custom lookup keyed on the attribute.
- **Services priced per hour or day:** load the loaded cost per unit, for example blended
  hourly cost × (1 + overhead), or × 8 for a day. Compute it before loading; the cost book
  holds only the result.
- **Pass-through items** such as travel: cost close to price, so a low margin by design.

## Check before relying on margins

- **Subscriptions** `[inferred]`: the shipped formula multiplies unit cost by quantity
  only. For a term line whose `ItemNetTotalPrice` covers several billing
  periods, that compares one period's cost with several periods' revenue, and overstates
  margin.
    - Price a 36-month annual line and compare `Margin` with a hand calculation.
    - If it's wrong, either store the cost per term, or change the formula to multiply by
      the term count (`PricingTermCount`) in a procedure overlay (`expression-sets`).
- **Evergreen lines** are priced for the Evergreen default pricing term count in Salesforce
  Pricing Setup: at `1`, a $50/month line totals $50; left blank, the count comes from the
  line's start and end dates [Help: `ind.pricing_configure_proration_settings.htm`;
  [../proration-and-selling-models.md](../proration-and-selling-models.md)]. So the quote total,
  and a quote margin derived from it (row 6), count an Evergreen line for that many periods
  next to term lines at their full term `[inferred]`. A "full commitment" deal size or margin,
  such as monthly support counted over a comparison horizon, is a separate value: compute it
  outside the quote total (per-period amount × horizon), and don't compare it with
  quote-total margins.
- **Lines without a cost entry** are skipped by the filter, so they show no margin. They
  aren't zero-margin.
- **Table freshness:** a cost change without a refresh leaves the old cost.

## Price from cost and a target margin

A rule such as "price = unit cost ÷ (1 − target margin)", with the target entered per line,
needs `[inferred]`:
- a custom line field for the target margin, mapped into the context definition
  (`context-service`);
- a formula step that writes the input price from `ItemUnitCost__std` when the target is
  set, placed before the discount steps (`pricing-procedures` →
  `procedure-anatomy-and-ordering.md`).

The worked example: cost 58.46 at a 40% target → 97.43. Prove it with a reprice on a
scratch org before using it in a demo.

## Verify

```bash
sf data query -q "SELECT Product2.StockKeepingUnit, Quantity, TotalPrice, UnitCost, TotalCost, Margin, MarginAmount FROM QuoteLineItem WHERE QuoteId = '<quote>'" --target-org <sf_alias>
```

`UnitCost` equals the cost entry for that product and currency. `TotalCost` equals
`UnitCost × Quantity`. `Margin` equals `(TotalPrice − TotalCost) / TotalPrice`. Then repeat
the query on the order.

## Open questions

- OPEN: how a cost-based target price (unit cost ÷ (1 − target margin), above) interacts
  with a later Manual Discount in the same procedure. Manual Discount reads the previous
  `NetUnitPrice` as its input (`../../pricing-procedures/elements/manual-discount.md`), so a
  rep discount after the target-price step may take the line below its target margin. Whether
  the target should act as a floor, or be re-applied after discounts, is untested.
