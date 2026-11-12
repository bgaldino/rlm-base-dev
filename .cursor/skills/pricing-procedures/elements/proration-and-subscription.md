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
into the line total and the per-unit subscription price. [Help] Selling models, proration policies
and Help's period examples: [`../../pricing-setup/proration-and-selling-models.md`](../../pricing-setup/proration-and-selling-models.md).

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
| Effective To | `EffectiveTo` | input var | conditional | [Core] optional on its own, but the line fails unless `EffectiveTo` **or** (`SubscriptionTerm` and `SubscriptionTermUnit`) has a value.  Repo binds `itemTransientEndDate` on the evergreen step and `EffectiveTo` on the term-defined step. [Repo] |
| Proration Period | `ProrationPeriod` | input var | yes | Billing period unit; repo binds `PricingTermUnit`. Help example binds `PricingTermUnit` too. [Help][Repo] |
| Start Proration Period | `StartProrationPeriod` | input var | yes | `AlignToCalendar`, `Anniversary`, `DayOfPeriod`, `LastDayOfPeriod`: the full set accepted by the period-boundary enum and its error text [Core]. Help (`ind.pricing_subscription_variables.htm`) names the fourth value `EndOfPeriod`, which is not in that enum: bind `LastDayOfPeriod`. |
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
`ProrationMultiplier` is Numeric. Quantity, Proration Multiplier and Net Unit Price as required inputs of Subscription Price: [inferred] from Help and the shipped steps (core parameter declarations for this element were not re-read).

## Placement and ordering
- Proration must run **before** Subscription Price in the same line scope: the multiplier
  must exist when Subscription Price reads it. [Repo: in the term-defined and evergreen proration groups Proration is seq 2 and Subscription seq 3]
- Both sit after the discount/price steps they depend on (Net Unit Price must be final
  before Subscription Price multiplies). Cross-element order: `../procedure-anatomy-and-ordering.md`.
- Repo pattern: separate `ListGroup` parents per selling model, each holding a BKM pair, with
  a filter on the line's selling model type. [Repo]
  - `Apply prorated pricing to term-defined lines` -> proration multiplier + prorated price.
  - `Apply prorated pricing to evergreen lines` -> same pair, but `EffectiveTo` is bound to `itemTransientEndDate`.
  - A fallback Subscription Price step for lines with neither type (constant multiplier 1).
- Pricing Setting must come first to supply the line item and price waterfall. [Help]

## Rules and limits
- [Core] Per-line input validation (error codes): end date or term+unit missing
  (`END_DATE_MISSING`: logged when neither an end date nor a subscription term with its unit is provided; a term of 0 counts as not provided [Core]), invalid `ProrationPeriod`
  (`INVALID_PRORATION_PERIOD`: "Enter a valid period either Months, Quarterly, Semi-Annual or Annual." Fires when the bound value is not a selling-model term unit; the check accepts Daily, Weekly, Months, Quarterly, Semi-Annual and Annual even though the message lists only four. Checks run in order: end date, `ProrationPeriod`, `StartProrationPeriod`, then the optional ones [Core]), invalid
  `StartProrationPeriod` (`INVALID_PERIOD_BOUNDARY`: "Enter a start proration period with one of these values: AlignToCalendar, Anniversary, DayOfPeriod, or LastDayOfPeriod." [Core]), invalid `SellingModelType` (`INVALID_SELLING_MODEL_TYPE`: Evergreen, OneTime or TermDefined [Core]), month
  (`INVALID_PERIOD_BOUNDARY_MONTH`: "Enter a start month." [Core]), term unit, time period. The line is logged as failed and not prorated.
  `ProrationPeriod` and `SubscriptionTermUnit` are checked against the selling model term units.
- [Core] **One Time and Evergreen shortcut:** if `SellingModelType` is One Time or Evergreen and the
  Pricing Setup default term count is set, the multiplier is that default (as text) and the engine is
  not called. Evergreen with no default is prorated normally; One Time with no default is **not**
  prorated (no multiplier produced by the engine). Skipped lines are ignored. The shortcut runs only
  after the input checks above pass, and only when a `SellingModelType` value is bound: a line with
  no selling-model tag is always prorated by the engine. The defaults are read once per step run
  and are set per type (Evergreen, One Time) in Pricing Setup. [Core]
- Proration policy applies only to **term-defined or evergreen** selling models. [Help: `ind.pricing_create_a_proration_policy.htm`]
- Setup -> Salesforce Pricing Setup: default **pricing term count** for Evergreen and One Time
  (numeric). Evergreen `1` = price is one billing period. [Help: `ind.pricing_configure_proration_settings.htm`]
  A stored default for the line's type bypasses the proration engine and is used directly as the term
  count. Evergreen with no default: the count is computed from the dates. One Time with no default:
  the Proration step gives the line no multiplier, so it is not prorated there; Help's "blank =
  computed dynamically" does not hold for One Time [Platform behaviour, traced].
- Month precision [Help: `ind.pricing_proration_variables.htm`] says a partial month is rounded to the nearest whole
  number in that mode. Traced: with Allow Partial Proration Periods off the count is whole periods (a touched partial
  period counts as 1); with it on, only the first and last period are fractional (days used over that period's actual
  days, e.g. 15 of 30 = 0.5) and interior periods stay whole [Platform behaviour, traced, annual frequency]. Rounding to
  the nearest whole number was not traced and is unresolved. Month-plus-day proration is supported for any frequency. [Help]
- Remainder Strategy (policy): put the rounding remainder in the first or last period so
  period amounts sum to the original ($100/3 -> 33.34/33.33/33.33 or 33.33/33.33/33.34). [Help]
- If "Allow partial proration periods" is off, the engine charges the full pricing period. [Help]
- Leap years: end-of-month anniversaries move to the latest valid day of the next period. [Help: leap-year examples]
- Permission to build: Salesforce Pricing Design Time. [Help]
- Pricing Setup term counts are numeric only; One Time `12` = the price covers 12 periods. Policy: App Launcher > Proration Policies > New, type Standard Time Periods; tick Include in Output on element outputs. [Help]

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

DayOfPeriod (day 5, month February): partial allowed 314/365 -> $688.22; not allowed 1.0 -> $800.00. Weekly (DayOfPeriod 1=Monday..7=Sunday): 75 days / 7 = 10.71 weeks, $12.01 x 12 x 10.71 = $1,543.36 per Help (the product as written is $1,543.53, so Help rounds differently or has a typo). [Help]
Price = list x term count. Other articles: `ind.pricing_semi_annual_proration_examples.htm`,
`ind.pricing_quarterly_proration_examples.htm`, `ind.pricing_monthly_proration_examples.htm`,
`ind.pricing_annual_proration_examples_for_leap_years.htm`,
`ind.pricing_monthly_proration_examples_for_leap_years.htm`, `ind.pricing_weekly_proration.htm`.
Simple case: $150/month, Dec 18-31 2021 = 14/31 = 0.4516 -> $67.74; Apr 18-Dec 17 2021 = 8 full months -> $1,200; qty 5 leap-year: Feb 10-May 9 2024 -> $2,234.98, Jan 18-May 17 2024 -> $3,000. [Help]

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
  <!-- Quantity<-LineItemQuantity, ProrationMultiplier<-PricingTermCount, NetUnitPrice<-NetUnitPrice;
       outputs TotalSubscriptionPrice->ItemNetTotalPrice, SubscriptionNetUnitPrice->NetUnitPrice;
       literals HideWaterfall=false, IsRealTime=false, sectionCount=0, selectedFunction=Get.
       Non-prorated groups: NetUnitPrice<-InputUnitPrice, total -> TotalLineAmount, unit -> InputUnitPrice -->
  <parentStep>Applyproratedpricingtotermdefinedlines</parentStep>
  <sequenceNumber>3</sequenceNumber>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
```
Sequence numbers are per parent group. Shipped in `RLM_DefaultPricingProcedure`: Proration = 2 and Subscription Price = 3 in each proration group; of the two non-prorated Subscription Price steps, the one for lines without term-defined or evergreen pricing is seq 3 and the one in the non-prorated term-defined/evergreen group is seq 2. [Repo]

## Shipped in this repo (snapshot)
| Procedure | Step name | What it does |
|---|---|---|
| `RLM_DefaultPricingProcedure` | `Calculateprorationmultiplierfortermdefinedlines` | Proration, `EffectiveTo<-EffectiveTo` |
| same | `Calculateprorationmultiplierforevergreenlines` | Proration, `EffectiveTo<-itemTransientEndDate` |
| same | `Calculateproratedpricefortermdefinedlines` / `...forevergreenlines` | Subscription Price |
| same | `Calculatesubscriptionpriceforlineswithouttermdefinedorevergreenpricing` | Subscription Price, constant multiplier |
| `RLM_PRM_DISTI_Pricing_Procedure`, `RLM_Revenue_Management_Recalc_Procedure` | same six steps, same parents, same sequence numbers (checked against both XML files) | Identical pattern |

Full list (all three procedures; parent group, seq): [Repo, checked against the XML]

| Step | actionType | Parent group | Seq |
|---|---|---|---|
| `Calculateprorationmultiplierfortermdefinedlines` | `Proration` | `Applyproratedpricingtotermdefinedlines` | 2 |
| `Calculateproratedpricefortermdefinedlines` | `SubscriptionPricing` | same | 3 |
| `Calculateprorationmultiplierforevergreenlines` | `Proration` | `Applyproratedpricingtoevergreenlines` | 2 |
| `Calculateproratedpriceforevergreenlines` | `SubscriptionPricing` | same | 3 |
| `Calculatesubscriptionpricefortermdefinedandevergreenlines` | `SubscriptionPricing` | `Applynonproratedpricingtotermdefinedandevergreenlines` | 2 |
| `Calculatesubscriptionpriceforlineswithouttermdefinedorevergreenpricing` | `SubscriptionPricing` | `Applynonproratedpricingforlineswithouttermdefinedorevergreenpricing` | 3 |

`RLM_Price_Distribution_Procedure`, `RLM_ProductDiscoveryPricingProcedure` and every other procedure under `force-app`, `post_procedureplans`, `post_prm_pricing`: none. Each of the three procedures above has 6 such steps; none carries a condition.

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

## Related
- `ind.qocal_ramp_schedule_with_trial_and_proration_segments.htm` covers the Create Ramp Schedule flow (TRIAL and PRORATED segment types), not this element; see ../../ramped-quotes/SKILL.md.
- Generic lifecycle (Connect CRUD, activation): `../../expression-sets/SKILL.md`.

## Open questions
- `END_DATE_MISSING` message text was not re-read in core; only the code is cited.

## Resolved disagreements
| Point | Help | Repo | Core | Winner |
|---|---|---|---|---|
| `SellingModelType` / `SubscriptionTermUnit` binding | `ProductSellingModel`, `ItemSubscriptionTermUnit` | `SellingModelType`, `PricingTermUnit` | parameter names fixed; bound tag is free | Both valid; Help example tags are samples |
| Net Unit Price binding | `ListPrice` | `NetUnitPrice` (prorated groups), `InputUnitPrice` (non-prorated) | parameter `NetUnitPrice` only | Bind the post-discount price (repo) |
| Parameters required | Help example maps Day/Month like the rest | n/a | Day/Month optional | Core |
| Blank One Time default | Blank = term count computed dynamically from dates (both types) | n/a | One Time, no default: no multiplier from the Proration step, not prorated [Platform behaviour, traced] | Core; Help's blank = computed does not hold for One Time |
| `ProductId`/`ProductSellingModelId` | n/a | assumed on Proration | not parameters | Core: drop |
