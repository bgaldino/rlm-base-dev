# Commitment-term discount (List Group + Formula-Based Pricing)

> Pattern file under `elements/`, like
> [`price-revision-compound-uplift.md`](price-revision-compound-uplift.md): it combines existing
> elements rather than documenting a new one. Release 264 / API v68.0. Sources: Help
> `ind.pricing_list_group_list_operation.htm`, `ind.pricing_formula_based_pricing.htm`,
> `ind.pricing_add_the_subscription_price_proration_element.htm`,
> `ind.product_catalog_product_selling_model.htm`,
> `ind.pricing_add_the_price_adjustment_matrix_element.htm`; dev guide
> `actions_obj_run_salesforce_headless_pricing.htm`; shipped `RLM_DefaultPricingProcedure`; a live
> run on a 264 scratch org (QuantumBit build) on 2026-11-10; real quotes and headless runs on a
> fresh 264 `ent-sb0` scratch org on 2026-11-11.
>
> Tags: `[Help: …]`, `[Dev guide: …]`, `[Repo: …]`, and `[Measured: 2026-11-10, 264]` for a
> result observed live on that org: a headless pricing run (request and response shapes in
> [`../runtime-and-observability.md`](../runtime-and-observability.md)), a describe, or a save.
> `[Measured: 2026-11-11, 264, fresh ent-sb0 scratch org]` marks the second run, which priced
> real quotes (Place Sales Transaction, configuration rules on, and a group ramp built in the
> quote UI) as well as headless requests.

A commitment-term discount gives an extra percentage off a subscription line because the customer
commits to a long term. The rule modeled here: **annual Term Defined subscriptions committed for 36
months or more get a further 4% off, applied after the line's other standard discounts; the
discounted net is rounded to the cent, then the 4% is applied, then the result is rounded again.**
Shorter terms and Evergreen lines are unchanged. One Time lines were not in the first run; a later
run priced them without error with criterion 11 in place (see [Open questions](#open-questions)).

Worked example (the golden test): list 18,000, 5% and 3% discounts → net 16,587.00 → × 0.96 →
**15,923.52**. A 24-month term stays at **16,587.00**.

## When to use it

- The 264 Help and dev-guide snapshots document no pricing element built for term-based or
  commitment-based discounts (Commitment Rate Adjustment is a rating element for
  commitment-based usage products [Help: `ind.rm_commitment_rate_adjustment.htm`]), so a term
  discount is built from general elements.
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
| `SellingModelType` | `SellingModelType` | The selling model type: One Time, Term-Defined or Evergreen [Help: `ind.product_catalog_product_selling_model.htm`]. The shipped filters compare it with `'TermDefined'` and `'Evergreen'` [Repo: `RLM_DefaultPricingProcedure`] |
| `PricingTermUnit` | `PricingTermUnit` | The selling model's pricing term unit; `Annual` for an annual subscription |
| `ItemSubscriptionTerm` | `SubscriptionTerm` | The line's subscription term, a number |
| `ItemSubscriptionTermUnit` | `SubscriptionTermUnit` | The unit of that term. The `QuoteLineItem` picklist offers `Months`, `Quarterly`, `Semi-Annual`, `Weekly`, `Annual` [Measured: 2026-11-10, 264, field describe] |
| `ItemPricingSource` | `PricingSource` | `LastTransaction` on lines priced from a prior transaction [Repo: shipped filter `Filterlineswithoutlasttransactionpricing`] |
| `NetUnitPrice` | `NetUnitPrice` | The running net unit price after the standard discounts |

The term is compared in its own unit, so the filter accepts either form of a 36-month commitment:
36 or more `Months`, or 3 or more `Annual`. Both were measured headless. On a saved quote line,
send the term in the selling model's unit; see
[Line inputs on real quotes](#line-inputs-on-real-quotes).

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
  returns an error [Help: `ind.pricing_list_group_list_operation.htm`]. Criterion 2 has no such
  guard, and `PricingTermUnit` must be null on a One Time selling model
  [Dev guide: `sforce_api_objects_productsellingmodel.htm`]. A bundle can mix One Time, Term
  Defined and Evergreen lines, since each child keeps its own selling model options
  ([product-catalog-modeling → Selling models inside bundles](../../product-catalog-modeling/selling-models-and-lifecycle.md#selling-models-inside-bundles)).
  As a precaution, add criterion 11, `PricingTermUnit` IsNotNull, ahead of the comparison it
  guards, as in Help's example (`{LineItem equals isNotNull} AND {LineItem equals 100}`):
  `1 AND 11 AND 2 AND 3 AND 4 AND 9 AND 10 AND ((5 AND 6) OR (7 AND 8))`. The filter does not stop at the first false
  criterion: it evaluates every criterion and treats one that reads an empty tag as unknown. If
  the result is the same with the unknown taken as true or as false, the filter returns that
  result; if the unknown would change the result, the pricing step fails with a missing-values
  error, and the filter returns false, failing the decision service [Platform behaviour, traced].
  That error path applies because resource-value defaulting is off for pricing. There is no org-level switch for it: defaulting is a property of the expression set itself, fixed when the set is created, and a pricing expression set cannot select it, so no setting changes this for pricing [Platform behaviour, traced]. (Where a process type allows defaulting and it is on, an empty value becomes false and never errors.) That a comparison
  on an empty tag yields unknown rather than throwing was inferred from the null branch, not read from
  the operator code. So, under those conditions, the guard works wherever it sits in the logic: a
  false `IsNotNull` makes the unknown criterion irrelevant. A compiled-expression filter path also
  exists in 264; it was traced to drop the row silently, without an error, when an empty value decides
  the outcome. Which path the shipped main filter takes is undetermined, so an unguarded empty field
  can be dropped silently or fail the step depending on the path. The overlay and the measured result
  below do not have the guard; the 2026-11-11 build did, and priced One Time lines without error
  ([Line inputs on real quotes](#line-inputs-on-real-quotes)). Without it, the live result is
  still open (see [Open questions](#open-questions)).
- Criterion 9 copies the shipped discount filters, which skip last-transaction lines so an amended
  or renewed line does not take a discount a second time [Repo: `RLM_DefaultPricingProcedure`,
  `Filterlineswithoutlasttransactionpricing`]. Without it, an amendment that keeps the prior net
  unit price would lose another 4%. That case was not measured.
- **What criterion 9 means for a renewal** (for example a 36-month renewal at +5%):
  - The shipped default prices a last-transaction line on its own path. When its `NetUnitPrice`
    is null, `ListContainer` (step 8) assigns `InputUnitPrice` to it, the setup Help gives for
    pricing from the last transaction [Help: `ind.qocal_set_up_price_amendments.htm`]. Every
    phase 7 adjustment group (17 to 23) filters on `ItemPricingSource NotEquals
    'LastTransaction'`, and the renewal uplift group (24) runs only on lines with
    `ItemPricingSource Equals 'LastTransaction'`, action `Renew`, a policy formula and no ramp
    [Repo: `RLM_DefaultPricingProcedure`;
    [`../../pricing-wiring/price-revision-cpi.md`](../../pricing-wiring/price-revision-cpi.md)].
    A last-transaction line with a contract price takes another path: step 13 sets its
    `InputUnitPrice` to `ItemContractPrice`, and group 26, after group 24, assigns
    `InputUnitPrice` to `NetUnitPrice` on lines with `ItemPricingSource Equals 'LastTransaction'`
    and `ItemContractPrice` not null [Repo: `RLM_DefaultPricingProcedure`,
    `Setinputunitpriceforlineswithcontractpricing`,
    `Setnetunitpriceforcontractedlasttransactionlines`].
  - Help: an uplift needs the asset's Pricing Source to be Last Transaction, and under Last
    Transaction Pricing should be applied after discounts; with a list-price source the uplift is
    ignored [Help: `ind.qocal_renewal_price_uplifts.htm`,
    `ind.qocal_consumer_price_index_and_uplifts_important_considerations.htm`]. With a
    CPI/Variable uplift, Help computes the renewal net unit price from the latest asset action
    source's change in subtotal divided by its change in quantity, times (1 + the uplift)
    [Help: `ind.qocal_consumer_price_index_and_price_uplifts.htm`]. Whether that price includes a
    4% the earlier sale took is not documented.
  - This repo stamps `LastTransaction` on every lifecycle asset whose source is blank [Repo: flow
    `RLM_Update_Asset_Pricing_Source_if_Price_Revision`], and the as-is renewal recorded in
    [`../../pricing-wiring/price-revision-cpi.md`](../../pricing-wiring/price-revision-cpi.md) →
    Expected results took the uplift, which group 24 applies only to last-transaction lines
    [Repo: measured 2026-10-29, 264, default procedure].
  - So, inferred from the filters and not measured: the uplift (group 24) and this group select
    disjoint lines. A renewal line from a Last Transaction asset gets **no term discount from
    this group**; it carries the 4% only if the price it starts from already includes it.
    Without a contract price it takes the uplift. With one, group 26 writes the contract price
    over the uplifted net, so it ends at the contract price without the uplift. A renewal line
    from a list-price asset takes no uplift and passes criterion 9, so it gets the 4% if its
    term meets the threshold (the renewal takes its term from the asset or the contract [Help:
    `ind.qocal_renew_assets.htm`]). As built, one renewal line does not get both.
  - Letting `Renew` lines through criterion 9 would reward a renewal's own commitment. If the
    price the renewal starts from already includes an earlier 4%, it would take the 4% a second
    time. Help's "uplifts after discounts" would put the group before group 24 rather than at
    28. Neither was built; see [Open questions](#open-questions).
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
- **Before** Proration and Subscription Price (phase 10). In the shipped default, Subscription Price
  (`Calculateproratedpricefortermdefinedlines`) reads `NetUnitPrice` and multiplies it by quantity
  and `PricingTermCount` into `ItemNetTotalPrice` [Repo: `RLM_DefaultPricingProcedure`; the Help
  example binds `ListPrice` instead, `ind.pricing_add_the_subscription_price_proration_element.htm`].
  So the formula only has to write `NetUnitPrice`: the line total follows (15,923.52 × 3 =
  47,770.56) [Measured: 2026-11-10, 264]. In a procedure whose Subscription Price reads `ListPrice`,
  it does not.
- Far ahead of DDS and the aggregates, so the tail rule does not apply
  ([`formula-based-pricing.md`](formula-based-pricing.md) → Placement).

## Rounding before a negotiated discount

The inner `ROUND(NetUnitPrice, 2)` above rounds the net to the cent before the term discount.
Some sources also round to the cent **before the negotiated (manual) discount**, so the rep's
percentage is taken from a cent-rounded price. Neither Help nor the repo places a rounding step
there: no shipped procedure has a `RoundingValues` step, and Help's example puts it after the
formula that produces the value ([`rounding-values.md`](rounding-values.md) → Placement and
ordering, Shipped). Treat the position as the source's requirement and model it like this:

- Add a Rounding Values step that rounds `NetUnitPrice` and writes it back, after the elements
  that produce the fractional price and before the Manual Discount groups (phase 7 in
  [`../procedure-anatomy-and-ordering.md`](../procedure-anatomy-and-ordering.md): `ManualDiscount`
  22 and the amount/percentage discounts 23). Manual Discount takes the previous `NetUnitPrice`
  as its input unit price ([`manual-discount.md`](manual-discount.md) → Configuration), so it then
  discounts the rounded value.
- Help says the element rounds the output of any pricing element in a procedure
  [Help: `ind.pricing_rounding_values.htm`], and core checks no position for it except the DDS
  tail rule ([`rounding-values.md`](rounding-values.md) → Feasibility). Fields, precision and
  multicurrency behavior are in that file.
- Inside a formula, round the operand instead, as step 2 of this pattern does.
- A Rounding Values step at that position was built and ran on 2026-11-11, and manual discounts
  after it priced as expected ([`rounding-values.md`](rounding-values.md) → Rules and limits).
  **Open — needs live verification:** a line whose net has a fractional cent going into the
  discount; check the discounted net and the waterfall entry.

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
Products: a QuantumBit Term Annual product (price book list 12,000 USD) on lines 1, 2, 4 and 5, and
an Evergreen product (list 420 USD) on line 3. Lines 1 to 4 pass
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

## Line inputs on real quotes

The run above passed the term inline. On real quotes (Place Sales Transaction; the last row is a
group ramp built in the quote UI)
[Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org]:

| Line as sent | Saved line | Result |
|---|---|---|
| Start and end dates, no term (a Term Defined Annual line, placed with System pricing and configuration method Force, configuration rules on; same result standalone and as a bundle component) | `SubscriptionTerm` null, unit `Annual` | Criterion 3 fails: the term-keyed discount step does not apply (the comparison requests also swapped the end date for term and unit) |
| `SubscriptionTerm` 36, unit `Months`, Annual selling model | Unit rewritten to `Annual`: 36 years, `PricingTermCount` 36 | Discount applied (through criteria 7 and 8, inferred from the saved unit), total over **36 terms** |
| `SubscriptionTerm` 3, unit `Annual` | As sent, `PricingTermCount` 3 | Discount applied, total over 3 terms: the correct shape |
| A segment line of a group ramp built in the quote UI | `SubscriptionTerm` 1, unit `Annual`, a ramp identifier | Criterion 8 fails: no discount unless criterion 14 below |

For a line that goes through the proration engine, the pricing term count is the number of periods in the selling model's term unit: the line's
`SubscriptionTerm` is read in that unit (36 on an Annual model is 36 annual periods, whatever unit
the line carries), and a line with no term has its count derived from its start and end dates
[Platform behaviour, traced]. An Evergreen or One Time line with a configured default term count takes that count directly, bypassing the engine; a One Time line with no default is not prorated [Platform behaviour, traced]. A dates-only line is therefore priced over its dates, but Place does not derive `SubscriptionTerm` from dates [Platform behaviour, traced]. The trace shows Place filling a missing term context tag with the selling model's pricing term when the line's selling model option is Term Defined, but not that fill reaching the saved line. In the measured requests (price book entry only, no selling model set on the line) the saved unit became the selling model's `Annual` but `SubscriptionTerm` stayed null: a dates-only Term Defined Annual line (System pricing, configuration method Force, rules on) priced from its dates (term count 3) and did not get the term-keyed discount step that the measured org's customised pricing procedure adds (not a shipped step), both standalone (net 17,100, vs 16,416 when the line was sent with `SubscriptionTerm` 3 and unit `Annual` instead of an end date) and as a bundle component (16,587 vs 15,923.52 on the same change) [Measured: 2026-11-11, 264, scratch]. Why the term was not filled was not established. Send the term explicitly.

So send every Term Defined line's term in its selling model's unit (3 `Annual` for 36 months on an
annual model). The `Months` criteria (5 and 6) were seen matching only in headless runs.

Optional criteria measured in the same build:

| # | Resource | Operator | Value | Purpose |
|---|---|---|---|---|
| 11 | `PricingTermUnit` | IsNotNull | | Guard for criterion 2 (see Configuration) |
| 12 | `<header switch tag>` | Equals | `true` | Discount only when a header checkbox is on |
| 13 | `<header switch tag>` | IsNotNull | | Guard for criterion 12 |
| 14 | `ItemRampIdentifier` | IsNotNull | | Let group-ramp segment lines through |

Logic: `1 AND 11 AND 2 AND 9 AND 10 AND 13 AND 12 AND ((3 AND 4 AND ((5 AND 6) OR (7 AND 8))) OR 14)`.

- With criterion 11, a One Time line alone, and One Time and Evergreen lines mixed with a matching
  line, priced unchanged with no line error (headless).
- The header switch was a `Quote` Checkbox mapped into the sales transaction context as a
  `SalesTransaction` tag of data type BOOLEAN
  ([`../../context-service/SKILL.md`](../../context-service/SKILL.md)); the line filter read it.
  A header-only Place PATCH of the switch (`pricingPref` `System`) did not reprice the lines;
  Reprice All in the line editor did. Other ways of changing the header were not measured.
- Criterion 14 admits every group-ramp segment line, whatever the ramp's length [inferred from the
  filter]. The group runs after the ramp uplift, so each segment took the discount on its uplifted
  net.

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
| A 36-month quote line is not discounted | The line has start and end dates but no `SubscriptionTerm` | Set `SubscriptionTerm` in the selling model's unit (3 `Annual`) ([Line inputs on real quotes](#line-inputs-on-real-quotes)) |
| Line total counts 36 terms | `SubscriptionTerm` 36 `Months` sent on an Annual selling model; Place saved it as 36 `Annual` | Same fix: 3 `Annual` |
| Group-ramp segment lines are not discounted | Each segment line carries a term of 1 | Add criterion 14 (`ItemRampIdentifier` IsNotNull) |
| A header switch change has no effect | A header-only Place PATCH did not reprice the lines | Reprice All in the line editor |
| Discount applied twice on an amendment | Criterion 9 removed | Keep `ItemPricingSource NotEquals 'LastTransaction'` |
| A 36-month renewal line gets the uplift but not the 4% | Criterion 9 skips lines from a Last Transaction asset, which this repo makes the default source | Expected as built (inferred, not measured); see criterion 9 → renewals |
| Totals do not move with the unit price | Group placed after the term pricing groups, or Subscription Price reads `ListPrice` | Move it before `Applyproratedpricingtotermdefinedlines`; bind Subscription Price's Net Unit Price to `NetUnitPrice` |
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

- One Time lines were not in the 2026-11-10 run. With criterion 11 in place they priced without
  error on 2026-11-11 ([Line inputs on real quotes](#line-inputs-on-real-quotes)).
  **Open — needs live verification:** what an unguarded criterion 2 (no criterion 11) does on a One
  Time line's null `PricingTermUnit`. Help says a null compared tag
  returns an error, but what the error looks like, was not measured. The condition logic does not
  short-circuit, so ordering does not keep criterion 2 from being evaluated; it is the unknown-value
  rule above that decides whether the null matters, on the legacy path; the compiled path may drop the row silently (path undetermined) [Platform behaviour, traced]. Price a One
  Time line, alone and inside a mixed bundle, through the clone with and without criterion 11.
  Until then keep criterion 11, placed before criterion 2.
- What a Place-created line and a UI group-ramp segment line carry is measured
  ([Line inputs on real quotes](#line-inputs-on-real-quotes)). Which `SubscriptionTermUnit` the
  line editor writes when a rep adds a line by hand was not measured; check a real quote line
  before relying on one.
- The amendment and renewal behavior (criterion 9) was not measured. **Open — needs live
  verification:** renew, with a +5% uplift, one 36-month asset that took the 4% and one shorter
  asset renewed for 36 months, and price the renewal lines through the clone. On an as-is renewal
  the parent `NetUnitPrice` is null and the price sits on `QuoteLineDetail`
  ([`../../pricing-wiring/price-revision-cpi.md`](../../pricing-wiring/price-revision-cpi.md)), so
  read `NetUnitPrice` there, or on the lines of a headless response. Check whether the last
  transaction price the uplift starts from includes the original 4%, and whether the second line
  gets no term discount, as the filters imply. Repeat with a contract price on the line to check
  that it ends at the contract price without the uplift. Also
  open: whether a renewal should earn the 4% at all, and if so how to avoid taking it twice when
  the starting price already includes an earlier 4%. That is a business rule to settle with the
  source; no design for it was built or measured. The headless response did
  carry a waterfall entry for the formula step (input `NetUnitPrice` 16,587 on line 1); how it
  shows in the quote's waterfall UI was not checked.
