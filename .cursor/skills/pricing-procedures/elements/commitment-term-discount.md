# Commitment-term discount (List Group + Formula-Based Pricing)

> Pattern file under `elements/`, like
> [`price-revision-compound-uplift.md`](price-revision-compound-uplift.md): it combines existing
> elements rather than documenting a new one. Release 264 / API v68.0. Sources: Help
> `ind.pricing_list_group_list_operation.htm`, `ind.pricing_formula_based_pricing.htm`,
> `ind.pricing_add_the_subscription_price_proration_element.htm`,
> `ind.product_catalog_product_selling_model.htm`,
> `ind.pricing_add_the_price_adjustment_matrix_element.htm`; dev guide
> `actions_obj_run_salesforce_headless_pricing.htm`; shipped `RLM_DefaultPricingProcedure`; a live
> run on a 264 scratch org (QuantumBit build) on 2026-11-10.
>
> Tags: `[Help: …]`, `[Dev guide: …]`, `[Repo: …]`, and `[Measured: 2026-11-10, 264]` for a
> result observed through headless pricing on that org (request and response shapes below).

A commitment-term discount gives an extra percentage off a subscription line because the customer
commits to a long term. The rule modeled here: **annual Term Defined subscriptions committed for 36
months or more get a further 4% off, applied after the line's other standard discounts; the
discounted net is rounded to the cent, then the 4% is applied, then the result is rounded again.**
Shorter terms and other selling models are unchanged.

Worked example (the golden test): list 18,000, 5% and 3% discounts → net 16,587.00 → × 0.96 →
**15,923.52**. A 24-month term stays at **16,587.00**.

## When to use it

- The 264 Help and dev-guide snapshots document no native term-based or commitment-based
  adjustment element, so a term discount is built from general elements.
- Use this pattern (route b, a filter plus a formula) when the rule is one or a few fixed
  thresholds with a fixed percentage. It needs no decision table, recipe mapping, custom field or
  context change: every tag it reads is standard [Measured: 2026-11-10, 264].
- Use route (a), a Price Adjustment Matrix over a custom decision table, when business users must
  maintain many term bands as data. See [Route (a)](#route-a-price-adjustment-matrix) below.

## Inputs it reads

All are standard tags on the `SalesTransactionItem` node of the sales transaction context
[Repo: `RLM_SalesTransactionContext` describe; Measured: 2026-11-10, 264].

| Tag | Context attribute | What it carries |
|---|---|---|
| `SellingModelType` | `SellingModelType` | `TermDefined`, `Evergreen` or `OneTime` (the selling model type) [Help: `ind.product_catalog_product_selling_model.htm`] |
| `PricingTermUnit` | `PricingTermUnit` | The selling model's pricing term unit; `Annual` for an annual subscription |
| `ItemSubscriptionTerm` | `SubscriptionTerm` | The line's subscription term, a number |
| `ItemSubscriptionTermUnit` | `SubscriptionTermUnit` | The unit of that term. The `QuoteLineItem` picklist offers `Months`, `Quarterly`, `Semi-Annual`, `Weekly`, `Annual` [Measured: 2026-11-10, 264, field describe] |
| `ItemPricingSource` | `PricingSource` | `LastTransaction` on lines priced from a prior transaction [Repo: shipped filter `Filterlineswithoutlasttransactionpricing`] |
| `NetUnitPrice` | `NetUnitPrice` | The running net unit price after the standard discounts |

The term is compared in its own unit, so the filter accepts either form of a 36-month commitment:
36 or more `Months`, or 3 or more `Annual`. Both were measured.

## Configuration

One top-level List Group with two children [Help: `ind.pricing_list_group_list_operation.htm`:
the filter must be the first child, one filter per group].

**1. List Operation (filter), `AdvancedListFilter`, child 1.** Condition logic
`1 AND 2 AND 3 AND 4 AND 9 AND 10 AND ((5 AND 6) OR (7 AND 8))`:

| # | Resource | Operator | Value |
|---|---|---|---|
| 1 | `SellingModelType` | Equals | `'TermDefined'` |
| 2 | `PricingTermUnit` | Equals | `'Annual'` |
| 3 | `ItemSubscriptionTerm` | IsNotNull | |
| 4 | `ItemSubscriptionTermUnit` | IsNotNull | |
| 5 | `ItemSubscriptionTermUnit` | Equals | `'Months'` |
| 6 | `ItemSubscriptionTerm` | GreaterThanOrEquals | `36` |
| 7 | `ItemSubscriptionTermUnit` | Equals | `'Annual'` |
| 8 | `ItemSubscriptionTerm` | GreaterThanOrEquals | `3` |
| 9 | `ItemPricingSource` | NotEquals | `'LastTransaction'` |
| 10 | `NetUnitPrice` | IsNotNull | |

- The not-null criteria (3, 4, 10) follow the Help rule that a null tag compared in a filter
  returns an error [Help: `ind.pricing_list_group_list_operation.htm`].
- Criterion 9 copies the shipped discount filters, which skip last-transaction lines so an amended
  or renewed line does not take a discount a second time [Repo: `RLM_DefaultPricingProcedure`,
  `Filterlineswithoutlasttransactionpricing`]. Without it, an amendment that keeps the prior net
  unit price would lose another 4%. That case was not measured.
- Nested parentheses in the condition logic save and evaluate as expected
  [Measured: 2026-11-10, 264].

**2. Formula-Based Pricing, `FormulaBasedPricing`, child 2.** One formula:

| Parameter | Type | Value |
|---|---|---|
| `formula-section-0-input` | `Formula` | `ROUND(ROUND(NetUnitPrice, 2) * 0.96, 2)` |
| `formula-section-0-output` | `Parameter` (output) | `NetUnitPrice` |
| `formulaSectionCount` | `Literal` | `1` |
| `selectedFunction`, `sectionCount`, `HideWaterfall`, `IsRealTime` | `Literal` | `Get`, `0`, `false`, `false` (shipped boilerplate) |

- Writing `NetUnitPrice` from a formula that reads `NetUnitPrice` is accepted; the shipped
  discount elements do the same [Repo: `ManualDiscount` steps read and write `NetUnitPrice`;
  Measured: 2026-11-10, 264].
- `ROUND(x, 2)` rounds half up at the second decimal: 10.005 became 10.01, then
  10.01 × 0.96 = 9.6096 became 9.61. A single rounding (10.005 × 0.96 = 9.6048) would give 9.60,
  so the measured 9.61 shows both roundings ran [Measured: 2026-11-10, 264].
- To make the rate configurable, put `0.96` (or the percentage) in a Numeric constant
  (overlay `addVariables`) and reference it in the formula. Not measured.

## Placement

Insert the List Group as a **top-level step after the last-transaction group and before the term
pricing groups**: in the shipped default, between `Filterlineswithlasttransactionpricingandassignnettotalprice`
(27) and `Applyproratedpricingtotermdefinedlines` (28), so it becomes 28 and the rest shift down
[Repo: phase table in [`../procedure-anatomy-and-ordering.md`](../procedure-anatomy-and-ordering.md),
phases 9 and 10].

- After phase 7 (attribute, bundle, volume, manual and amount/percentage discounts), so the 4% is
  taken from the already discounted net, as the rule requires.
- After phase 8 (price revision): the 4% is taken from the revised price. Moving it before price
  revision only changes cent rounding, since both are multiplicative. Not measured.
- **Before** Proration and Subscription Price (phase 10). Subscription Price multiplies the net unit
  price by quantity and `PricingTermCount` into `ItemNetTotalPrice`
  [Help: `ind.pricing_add_the_subscription_price_proration_element.htm`], so the formula only has to
  write `NetUnitPrice`: the line total follows (15,923.52 × 3 = 47,770.56) [Measured: 2026-11-10, 264].
- Far ahead of DDS and the aggregates, so the tail rule does not apply
  ([`formula-based-pricing.md`](formula-based-pricing.md) → Placement).

## Overlay shape

Applied to the clone with `apply_expression_set_overlay.py --no-cascade --confirm`; captured shape
(boilerplate envelope flags omitted, same as the shipped steps) [Measured: 2026-11-10, 264]:

```json
{
  "expressionSetApiName": "<clone>",
  "versionApiName": "<clone>_V1",
  "addSteps": [
    { "name": "RLMTermDiscountSpikeGroup", "label": "Apply Commitment Term Discount",
      "stepType": "ListGroup",
      "placement": { "afterStep": "Filterlineswithlasttransactionpricingandassignnettotalprice" } },
    { "name": "RLMTermDiscountSpikeFilter", "label": "Annual Term Lines 36 Months Or More",
      "stepType": "AdvancedListFilter", "parentStep": "RLMTermDiscountSpikeGroup", "sequenceNumber": 1,
      "advancedCondition": {
        "conditionLogic": "1 AND 2 AND 3 AND 4 AND 9 AND 10 AND ((5 AND 6) OR (7 AND 8))",
        "criteria": [
          { "sequenceNumber": 1, "sourceFieldName": "SellingModelType", "operator": "Equals", "value": "'TermDefined'", "valueType": "Literal" },
          { "sequenceNumber": 2, "sourceFieldName": "PricingTermUnit", "operator": "Equals", "value": "'Annual'", "valueType": "Literal" },
          { "sequenceNumber": 3, "sourceFieldName": "ItemSubscriptionTerm", "operator": "IsNotNull" },
          { "sequenceNumber": 4, "sourceFieldName": "ItemSubscriptionTermUnit", "operator": "IsNotNull" },
          { "sequenceNumber": 5, "sourceFieldName": "ItemSubscriptionTermUnit", "operator": "Equals", "value": "'Months'", "valueType": "Literal" },
          { "sequenceNumber": 6, "sourceFieldName": "ItemSubscriptionTerm", "operator": "GreaterThanOrEquals", "value": "36", "valueType": "Literal" },
          { "sequenceNumber": 7, "sourceFieldName": "ItemSubscriptionTermUnit", "operator": "Equals", "value": "'Annual'", "valueType": "Literal" },
          { "sequenceNumber": 8, "sourceFieldName": "ItemSubscriptionTerm", "operator": "GreaterThanOrEquals", "value": "3", "valueType": "Literal" },
          { "sequenceNumber": 9, "sourceFieldName": "ItemPricingSource", "operator": "NotEquals", "value": "'LastTransaction'", "valueType": "Literal" },
          { "sequenceNumber": 10, "sourceFieldName": "NetUnitPrice", "operator": "IsNotNull" }
        ] } },
    { "name": "RLMTermDiscountSpikeFormula", "label": "Apply 4 Percent Term Discount",
      "stepType": "BusinessKnowledgeModel", "actionType": "FormulaBasedPricing",
      "parentStep": "RLMTermDiscountSpikeGroup", "sequenceNumber": 2,
      "customElement": { "parameters": [
        { "name": "formula-section-0-input", "type": "Formula", "input": true, "output": false,
          "value": "ROUND(ROUND(NetUnitPrice, 2) * 0.96, 2)" },
        { "name": "formulaSectionCount", "type": "Literal", "input": true, "output": false, "value": "1" },
        { "name": "selectedFunction", "type": "Literal", "input": true, "output": false, "value": "Get" },
        { "name": "sectionCount", "type": "Literal", "input": true, "output": false, "value": "0" },
        { "name": "HideWaterfall", "type": "Literal", "input": true, "output": false, "value": "false" },
        { "name": "IsRealTime", "type": "Literal", "input": true, "output": false, "value": "false" },
        { "name": "formula-section-0-output", "type": "Parameter", "input": false, "output": true,
          "value": "NetUnitPrice" }
      ] } }
  ]
}
```

No `addVariables` and no `externalDependencies`: every reference is a standard tag
([`../../expression-sets/authoring-and-overlays.md`](../../expression-sets/authoring-and-overlays.md)
→ three scopes). `validate_expression_set.py --overlay` reports no issues.

## Measured result

A disposable clone of `RLM_DefaultPricingProcedure` with the overlay above, priced through
`runSalesforceHeadlessPricing` with the procedure named (see
[`../runtime-and-observability.md`](../runtime-and-observability.md) → API-based verification).
Product: a QuantumBit Term Annual product (price book list 12,000 USD); each line passes
`UnitPrice` 18,000 and `Discount` 7.85, which the shipped procedure uses as the input unit price and
the percentage discount. 18,000 × (1 − 0.0785) = 16,587.00, the same pre-term net as 5% then 3%
(18,000 × 0.95 × 0.97). Start 2026-11-10, quantity 1 [Measured: 2026-11-10, 264].

| Line | Selling model | Term | Clone `NetUnitPrice` | Clone `NetTotalPrice` | Default procedure `NetUnitPrice` |
|---|---|---|---|---|---|
| 1 | Term Defined, Annual | 36 Months, end 2029-11-09 | **15,923.52** | 47,770.56 (× 3 terms) | 16,587.00 |
| 2 | Term Defined, Annual | 24 Months, end 2028-11-09 | **16,587.00** | 33,174.00 (× 2) | 16,587.00 |
| 3 | Evergreen, Annual | 36 Months, no end date | **16,587.00** | 16,587.00 (× 1) | 16,587.00 |
| 4 | Term Defined, Annual | 3 Annual, end 2029-11-09 | **15,923.52** | 47,770.56 (× 3) | 16,587.00 |
| 5 | Term Defined, Annual | 36 Months, `UnitPrice` 10.005, no discount | **9.61** | 28.83 (× 3) | 10.005 |

Lines 1 and 2 reproduce the golden test exactly. Line 3 shows the filter keys on the selling model
type, not the term. Before the overlay the clone returned 16,587.00 on lines 1 to 4, as the default
does, so the difference comes from the new group alone.

## Verify

1. Price a matching and a non-matching line through the clone (headless pricing as above, or
   Simulate in the builder) and compare `NetUnitPrice` against your golden numbers.
2. Price the same payload through the procedure the org runs, to confirm the baseline.
3. Re-price a real quote only after the clone is promoted; then query
   `NetUnitPrice` and `TotalPrice` on `QuoteLineItem`.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| A 36-month line is not discounted | Its `SubscriptionTermUnit` is not `Months` or `Annual`, or `PricingTermUnit` is not `Annual` | Check the line's unit; add a criterion pair for the unit you sell in |
| Discount applied twice on an amendment | Criterion 9 removed | Keep `ItemPricingSource NotEquals 'LastTransaction'` |
| Totals do not move with the unit price | Group placed after the term pricing groups | Move it before `Applyproratedpricingtotermdefinedlines` |
| Off by a cent | Single `ROUND`, or no `ROUND` | Keep both: `ROUND(ROUND(NetUnitPrice, 2) * 0.96, 2)` |

## Route (a): Price Adjustment Matrix

When the bands must be data (for example 12–23 months 2%, 24–35 months 3%, 36+ months 4%), use a
Price Adjustment Matrix over a custom decision table whose input columns are keyed on the term
[Help: `ind.pricing_add_the_price_adjustment_matrix_element.htm`,
`ind.pricing_calculate_product_prices_using_price_adjustment_matrix.htm`]. It needs a decision table
registered on the pricing recipe and refreshed after each band change, and each line must resolve to
exactly one row unless Output Resolution is on
([`price-adjustment-matrix.md`](price-adjustment-matrix.md)). Make the bands non-overlapping.
**Open — needs live verification:** this route was not built or measured here, because route (b)
expressed the rule.

## Open questions

- Which `SubscriptionTermUnit` the quote line editor writes for an annual Term Defined line was not
  measured; the filter accepts both `Months` and `Annual`. Check a real quote line before relying
  on one.
- The amendment and renewal behavior (criterion 9) and the waterfall entry for the formula step
  were not measured; the headless runs skipped the waterfall.
