# Proration (`Proration`) and Subscription Price (`SubscriptionPricing`)

> Release 264 / API v68.0. Sources: `ind.pricing_subscription_pricing_proration.htm`,
> `ind.pricing_add_the_subscription_price_proration_element.htm`,
> `ind.pricing_configure_proration_settings.htm`, `ind.pricing_create_a_proration_policy.htm`,
> `ind.pricing_proration_variables.htm`, `ind.pricing_subscription_variables.htm`,
> `ind.pricing_*_proration_examples*.htm`, `ind.pricing_configure_product_selling_model_for_your_products.htm`;
> shipped XML: `RLM_DefaultPricingProcedure` (also PRM Disti and Recalc procedures);
> verified against core 264 (formal parameters, input validation, One Time / Evergreen shortcut).

Two paired elements. **Proration** turns a date range + billing period into a multiplier
(`PricingTermCount`). **Subscription Price** multiplies unit price x quantity x that multiplier
into the line total and the per-unit subscription price. [Help]

## When to use it
- Use for time-based pricing of term-defined and evergreen subscription lines: mid-period
  start, cancel, amend. [Help: `ind.pricing_subscription_pricing_proration.htm`]
- Always pair them: Proration emits `PricingTermCount`, Subscription Price consumes it. [Help]
- One-time lines: no proration needed; the repo still routes them through a Subscription Price
  step with a constant multiplier of 1 (see Metadata shape). [Repo]
- Don't use it to apply discounts or uplifts; see [Price Revision](./price-revision.md).

## Configuration

### Proration element
| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Effective From | `EffectiveFrom` | input var | yes | Start of the priced period. [Help][Repo] |
| Effective To | `EffectiveTo` | input var | conditional | [Core] optional on its own, but the line fails unless `EffectiveTo` **or** (`SubscriptionTerm` and `SubscriptionTermUnit`) has a value.  Repo binds `itemTransientEndDate` on the term-defined step and `EffectiveTo` on the other. [Repo] |
| Proration Period | `ProrationPeriod` | input var | yes | Billing period unit; repo binds `PricingTermUnit`. Help example binds `PricingTermUnit` too. [Help][Repo] |
| Start Proration Period | `StartProrationPeriod` | input var | yes | `AlignToCalendar`, `Anniversary`, `DayOfPeriod`, `EndOfPeriod`. [Help: `ind.pricing_subscription_variables.htm`] |
| Start Proration Period Day | `StartProrationPeriodDay` | input var | no [Core] | Used only when Start Proration Period = `DayOfPeriod`. [Help] |
| Start Proration Period Month | `StartProrationPeriodMonth` | input var | no [Core] | Same; annual only. [Help] |
| Allow Partial Proration Periods | `AllowPartialProrationPeriods` | input var | yes | False = partial usage rounds up to a full period. [Help] |
| Selling Model Type | `SellingModelType` | input var | no [Core] | Validated only when set (must be a valid selling model type). Help binds the tag `ProductSellingModel`, repo binds `SellingModelType`: the parameter name is fixed, the bound tag is your choice; either works if the tag carries the type. [Help][Repo][Core] |
| Subscription Term | `SubscriptionTerm` | input var | no [Core] (see Effective To) | Repo binds `ItemSubscriptionTerm`. [Repo] |
| Subscription Term Unit | `SubscriptionTermUnit` | input var | no [Core] | Same bound-tag choice: repo `PricingTermUnit`, Help `ItemSubscriptionTermUnit`. Must be a valid term unit when set. [Core] |
| Time Period | `TimePeriod` | input var | no | [Core] Offered only when the org may customize proration time periods; validated when set. Not shipped. |
| Proration Multiplier | `ProrationMultiplier` | output var | yes | Repo binds `PricingTermCount`. Tick Include in Output. [Help][Repo] |
| (Real time) | `IsRealTime` | literal | no | `false` in repo. [Repo] |


### Subscription Price element
| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Quantity | `Quantity` | input var | yes | `LineItemQuantity`. [Help][Repo] |
| Proration Multiplier | `ProrationMultiplier` | input var | yes | `PricingTermCount`, or a Literal-style constant `PricingTermCountValueOneConstant` for no-proration lines. [Help][Repo] |
| Net Unit Price | `NetUnitPrice` | input var | yes | Unit price input. Help binds `ListPrice`; repo binds `InputUnitPrice` / `NetUnitPrice` (post-discount price). [Help vs Repo] |
| Total Subscription Price | `TotalSubscriptionPrice` | output var (Currency) | yes | Repo binds `ItemNetTotalPrice` or `TotalLineAmount`. [Help][Repo] |
| Subscription Net Unit Price | `SubscriptionNetUnitPrice` | output var | yes | Repo binds `InputUnitPrice` / `NetUnitPrice`. [Repo] |
| Hide waterfall | `HideWaterfall` | literal | no | `false` in repo. [Repo] |
| (Real time) | `IsRealTime` | literal | no | `false`. [Repo] |

`ProductId` / `ProductSellingModelId` are **not** parameters of either element [Core]; the shipped
steps do not carry them (they appear on ListPrice, discount and bundle steps, where lookup columns
become parameters). Proration has no lookup table. Extra outputs can be added in sections. [Core][Repo]
`ProrationMultiplier` is Numeric. Quantity and Net Unit Price are required inputs of Subscription Price. [Core]

## Placement and ordering
- Proration must run **before** Subscription Price in the same line scope: the multiplier
  must exist when Subscription Price reads it. [Repo: Proration seq 2, Subscription seq 3 in each group]
- Both sit after the discount/price steps they depend on (Net Unit Price must be final
  before Subscription Price multiplies). Cross-element order: `../procedure-anatomy-and-ordering.md`.
- Repo pattern: separate `ListGroup` parents per selling model, each holding a BKM pair, with
  a filter on the line's selling model type. [Repo]
  - `Apply prorated pricing to term-defined lines` -> proration multiplier + prorated price.
  - `Apply prorated pricing to evergreen lines` -> same pair, `EffectiveTo` binding differs.
  - A fallback Subscription Price step for lines with neither type (constant multiplier 1).
- Pricing Setting must come first to supply the line item and price waterfall. [Help]

## Rules and limits
- [Core] Per-line input validation (message keys): end date or term+unit missing
  (`END_DATE_MISSING`), invalid `ProrationPeriod` (`INVALID_PRORATION_PERIOD`), invalid
  `StartProrationPeriod` (`INVALID_PERIOD_BOUNDARY`), invalid `SellingModelType`, month
  (`INVALID_PERIOD_BOUNDARY_MONTH`), term unit, time period. The line is logged as failed and not prorated.
  `ProrationPeriod` and `SubscriptionTermUnit` are checked against the selling model term units.
- [Core] **One Time and Evergreen shortcut:** if `SellingModelType` is One Time or Evergreen and the
  Pricing Setup default term count is set, the multiplier is that default (as text) and the engine is
  not called. Evergreen with no default is prorated normally; One Time with no default is **not**
  prorated (no multiplier produced by the engine). Skipped lines are ignored.
- Proration policy applies only to **term-defined or evergreen** selling models. [Help: `ind.pricing_create_a_proration_policy.htm`]
- Setup -> Salesforce Pricing Setup: default **pricing term count** for Evergreen and One Time
  (numeric). Blank = computed dynamically from start/end dates. Evergreen `1` = price is one
  billing period. [Help: `ind.pricing_configure_proration_settings.htm`]
- Month precision: whole months / term; a partial month is rounded to the nearest whole
  number in that mode. Month-plus-day proration is supported for any frequency. [Help: `ind.pricing_proration_variables.htm`]
- Remainder Strategy (policy): put the rounding remainder in the first or last period so
  period amounts sum to the original ($100/3 -> 33.34/33.33/33.33 or 33.33/33.33/33.34). [Help]
- If "Allow partial proration periods" is off, the engine charges the full pricing period. [Help]
- Leap years: end-of-month anniversaries move to the latest valid day of the next period. [Help: leap-year examples]
- Permission to build: Salesforce Pricing Design Time. [Help]

### Product selling model interplay
| Selling model type | Behavior |
|---|---|
| One Time | Not a subscription; no proration policy. Default term count from Pricing Setup. [Help] |
| Term-Defined | Has an end date; prorated by Effective From/To. [Help] |
| Evergreen | Recurs until cancelled; term count default from Pricing Setup, no end date. [Help] |
Assign a proration policy on the **Product Selling Model Option** (Price Book Entry -> Related ->
Product Selling Model Options), not on the product. Requires a price book entry. [Help]
`PricingTermUnit`, `StartProrationPeriod*`, `AllowPartialProrationPeriods` come from that option
via the context. [inferred from Help + repo bindings]

### Worked example (annual, anniversary vs calendar) [Help: `ind.pricing_annual_proration_examples.htm`]
Effective 2025-03-28 to 2026-02-04 (314 days), list price $800, Annual period.
| Start Proration Period | Allow partial | Term count | Price |
|---|---|---|---|
| Anniversary (Mar 28) | true | 314/365 = 0.860274 | $688.22 |
| Anniversary | false | 1.0 | $800.00 |
| AlignToCalendar (Jan 1) | true | 279/365 + 35/365 = 0.860274 | $688.22 |
| AlignToCalendar | false | each touched year = 1.0 -> 2.0 | $1,600.00 |
Price = list x term count. Other articles: `ind.pricing_semi_annual_proration_examples.htm`,
`ind.pricing_quarterly_proration_examples.htm`, `ind.pricing_monthly_proration_examples.htm`,
`ind.pricing_annual_proration_examples_for_leap_years.htm`,
`ind.pricing_monthly_proration_examples_for_leap_years.htm`, `ind.pricing_weekly_proration.htm`.
Simple case: $150/month, Dec 18-31 2021 = 14/31 = 0.4516 -> $67.74. [Help]

## Metadata shape
Parameters are `<customElement><parameters>` with `input`/`output`, `name`, `type`
(`Parameter` = variable binding, `Literal` = constant), `value`. [Repo]
```xml
<steps>
  <actionType>Proration</actionType>
  <customElement>
    <parameters><input>true</input><name>EffectiveFrom</name><output>false</output><type>Parameter</type><value>EffectiveFrom</value></parameters>
    <parameters><input>true</input><name>EffectiveTo</name><output>false</output><type>Parameter</type><value>EffectiveTo</value></parameters>
    <parameters><input>true</input><name>ProrationPeriod</name><output>false</output><type>Parameter</type><value>PricingTermUnit</value></parameters>
    <!-- StartProrationPeriod, StartProrationPeriodDay, StartProrationPeriodMonth,
         AllowPartialProrationPeriods, SellingModelType, SubscriptionTerm, SubscriptionTermUnit: same pattern -->
    <parameters><input>false</input><name>ProrationMultiplier</name><output>true</output><type>Parameter</type><value>PricingTermCount</value></parameters>
  </customElement>
  <name>Calculateprorationmultiplierfortermdefinedlines</name>
  <parentStep>Applyproratedpricingtotermdefinedlines</parentStep>
  <sequenceNumber>2</sequenceNumber>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
<steps>
  <actionType>SubscriptionPricing</actionType>
  <!-- Quantity<-LineItemQuantity, ProrationMultiplier<-PricingTermCount, NetUnitPrice<-InputUnitPrice;
       outputs TotalSubscriptionPrice->ItemNetTotalPrice, SubscriptionNetUnitPrice->NetUnitPrice -->
  <parentStep>Applyproratedpricingtotermdefinedlines</parentStep>
  <sequenceNumber>3</sequenceNumber>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
```
Sequence numbers are per parent group; shipped: Proration = 2, Subscription Price = 3. [Repo]

## Shipped in this repo (snapshot)
| Procedure | Step name | What it does |
|---|---|---|
| `RLM_DefaultPricingProcedure` | `Calculateprorationmultiplierfortermdefinedlines` | Proration, `EffectiveTo<-itemTransientEndDate` |
| same | `Calculateprorationmultiplierforevergreenlines` | Proration, `EffectiveTo<-EffectiveTo` |
| same | `Calculateproratedpricefortermdefinedlines` / `...forevergreenlines` | Subscription Price |
| same | `Calculatesubscriptionpriceforlineswithouttermdefinedorevergreenpricing` | Subscription Price, constant multiplier |
| `RLM_PRM_DISTI_Pricing_Procedure`, `RLM_Revenue_Management_Recalc_Procedure` | same pattern | |
Snapshot. Discover: `python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify
- Builder Simulate: set Effective From/To, Quantity; check the price waterfall shows the
  subscription step and the multiplier (Help table: $150, Dec 18-31 -> $67.74). [Help]
- Compare `Allow partial` true/false and each Start Proration Period against the examples. [Help]
- Persisted: `SELECT PricingTermCount, NetUnitPrice, TotalPrice FROM QuoteLineItem WHERE QuoteId='<id>'`
  (field availability inferred; confirm via describe).

## Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| Multiplier always 1 | No proration policy on the selling model option, or `AllowPartialProrationPeriods` false | Assign policy; tick allow partial [Help] |
| Total is unit price only | Subscription Price not reading `PricingTermCount`, or Proration runs after it | Fix binding and order |
| Wrong period boundaries | `StartProrationPeriod` mode mismatch (Anniversary vs AlignToCalendar) | Compare to examples |
| Day/Month ignored | Only used for `DayOfPeriod` | Set mode to DayOfPeriod [Help] |
| Evergreen price covers wrong # periods | Pricing Setup Evergreen term count | Set or blank it [Help] |
| Policy cannot be assigned | Selling model is One Time | Use term-defined or evergreen [Help] |

## Open questions
- Exact validation message text is a localized label; only the message keys are listed above.
- Generic lifecycle (Connect CRUD, activation): `../../expression-sets/SKILL.md`.

## Resolved disagreements
| Point | Help | Repo | Core | Winner |
|---|---|---|---|---|
| `SellingModelType` / `SubscriptionTermUnit` binding | `ProductSellingModel`, `ItemSubscriptionTermUnit` | `SellingModelType`, `PricingTermUnit` | parameter names fixed; bound tag is free | Both valid; Help example tags are samples |
| Net Unit Price binding | `ListPrice` | `InputUnitPrice` | parameter `NetUnitPrice` only | Bind the post-discount price (repo) |
| Parameters required | Day/Month marked required | | Day/Month optional | Core |
| `ProductId`/`ProductSellingModelId` | | assumed on Proration | not parameters | Core: drop |
