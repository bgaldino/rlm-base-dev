# Proration and Selling Models

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`. Release 264 / API v68.0. Sources:
> `ind.pricing_configure_product_selling_model_for_your_products.htm`,
> `ind.product_catalog_product_selling_model.htm`, `ind.product_catalog_create_a_product_selling_model.htm`,
> `ind.pricing_configure_proration_settings.htm`, `ind.pricing_create_a_proration_policy.htm`,
> `ind.pricing_proration_variables.htm`, `ind.pricing_subscription_variables.htm`,
> `ind.pricing_subscription_pricing_proration.htm`, `ind.pricing_*_proration_examples*.htm`,
> `ind.pricing_weekly_proration.htm`. Not live-verified except where tagged [Measured] (2026-11-11, a fresh 264
> `ent-sb0` scratch org).

Selling models say how a product is sold; proration settings and policies say how a partial period is
priced. The Proration and Subscription Price elements read them. Builder fields for the elements:
[`../pricing-procedures/elements/proration-and-subscription.md`](../pricing-procedures/elements/proration-and-subscription.md).

## When you need it

- A subscription starts, changes or ends mid-period and the charge must be partial.
- Setting up one-time, term-defined or evergreen products.
- Choosing where the rounding remainder lands, or whether a partial period bills in full.

## Set it up

**1. Product selling model** (Manage Product Catalog) [Help: `ind.product_catalog_create_a_product_selling_model.htm`]
1. Product Catalog Management app > Product Selling Models > New.
2. Name, selling model type, and (term-defined or evergreen) Pricing Term + Pricing Term Unit, e.g. Term-Defined 1 Year; Evergreen 1 Month.
3. Term-defined only: optionally **Automatically Renew Asset by Default**; the status is copied to quote and order lines and can be edited per line.
4. Set Status (Draft, Active, Inactive). It cannot return to Draft after Active/Inactive.

**2. <a name="default-term-counts"></a>Default term counts** (Salesforce Pricing Design Time) [Help: `ind.pricing_configure_proration_settings.htm`]
1. Setup > `Salesforce Pricing` > Salesforce Pricing Setup (`/lightning/setup/CorePricingSetup/home`), Proration Settings.
2. Fill **Evergreen** and/or **One Time** (numeric only). Help: blank = term count computed from start/end dates at run time. Core disagrees for One Time: with no default it is not prorated [Platform behaviour, traced: with no One Time value the line gets no multiplier from the Proration step]; test live ([element, Resolved disagreements](../pricing-procedures/elements/proration-and-subscription.md#resolved-disagreements)).

[Platform behaviour, traced] A default for a line's type bypasses the engine and is used directly as the term count; with no Evergreen default the count is computed from the dates; a stored value without a colon sets neither. This applies only when the line's selling model type is mapped; otherwise the line goes to the engine.

[Measured] **These two values have no API.** They were in none of the 11 settings types retrieved (among them
`IndustriesPricing`, `RevenueManagement`, `Quote`, `Order`, `Billing`, `ProductCatalogManagement` and
`SubscriptionManagement`), and no sObject or Tooling object for them appears in the global describes. This repo's
build doesn't set them. A fresh 264 org reads
**Evergreen 1, One Time 0** on that page.

[Repo] This repo's `RLM_DefaultPricingProcedure` (and any clone of it) sets the term count itself with two constants:
`OneTimePricingTermCountConstant` (0) on lines that are neither Term Defined nor Evergreen, and
`EvergreenPricingTermCountConstant` (1) on Evergreen lines without an end date or without partial proration. On that
procedure [Measured] an Evergreen line priced one period and a One-Time line carried `PricingTermCount` 0 while its
total was still unit price × quantity; those values come from the constants, which match the page's fresh-org values.
Whether the page affects Evergreen lines that reach the Proration step (an end date with partial proration on) wasn't
measured. A plan that states Evergreen prices per period depends on both: check the procedure's constants and read the
page in each target org.

**3. Proration policy** (Salesforce Pricing Design Time; needs a term-defined or evergreen selling model and a price book entry) [Help: `ind.pricing_create_a_proration_policy.htm`]
1. App Launcher > Proration Policies > New; name it.
2. Proration Policy Type = Standard Time Periods.
3. Remainder Strategy = First or Last pricing period.
4. Tick **Allow partial proration periods** to bill part periods pro rata; unticked, the full period is charged.

**4. Assign to a product**
1. App Launcher > Price Books > the price book > Price Book Entries > the product.
2. Related tab > Product Selling Model Options > New. Pick a term-defined or evergreen model, confirm the product, pick the policy, optionally tick **Default**.

## Fields and rules

| UI label | API name | Rules |
|---|---|---|
| Selling Model Type | `ProductSellingModel.SellingModelType` | One Time, Term-Defined (end date), Evergreen (until cancelled). [Help] |
| Pricing Term / Unit | `PricingTerm`, `PricingTermUnit` | Required for term-defined and evergreen. [Help] |
| Auto-renew | `DoesAutoRenewAssetByDefault` | Term-defined only. |
| Status | `Status` | Draft, Active, Inactive; no return to Draft. |
| Proration Policy Type | `ProrationPolicy.ProrationPolicyType` | `StandardTimePeriods`. |
| Remainder Strategy | `ProrationPolicy.RemainderStrategy` | First or last period; sums to the original amount ($100/3 = 33.34/33.33/33.33 or 33.33/33.33/33.34). [Help] |
| Allow partial proration periods | `ProrationPolicy.ArePartialPeriodsAllowed` | Off = full period charged. |
| Option -> policy | `ProductSellingModelOption.ProrationPolicyId` | Only on term-defined or evergreen options. [Help; ERD] |
| Evergreen / One Time default | Salesforce Pricing Setup; no API, UI only [Measured] | Evergreen 1 monthly at $50 = $50. [Help] Fresh 264 org: Evergreen 1, One Time 0. [Measured] |

Proration variables are Proration element inputs, bound to context tags that carry the selling model
option and policy values (inferred; see [the element](../pricing-procedures/elements/proration-and-subscription.md#product-selling-model-interplay)):
`StartProrationPeriod` (AlignToCalendar, Anniversary, DayOfPeriod, and `LastDayOfPeriod`, which Help
labels EndOfPeriod; bind `LastDayOfPeriod` [Core]), day/month for DayOfPeriod only. [Help: `ind.pricing_subscription_variables.htm`]
Multiplier = time used / total time in period; "month-plus-day" proration works for any frequency.
[Platform behaviour, traced] The count is day-based: the number of periods, where only the first and last
(partial) period count as days used / days in that full period, inclusive actual calendar days under an actual-days
policy (the default). The denominator is that period's real length, so a partial period in a leap year is over 366 (period boundaries inferred from measured values, all on contracts starting 1 January; for another start date measure one mid-period change first).
Partial periods off: whole periods only. A 30-day-month type counts a full month as 30 days (the 30/360 variant caps the day at 30; the actual-days-with-30-day-months variant counts partial months in actual days). The remainder strategy
changes the money split, not the count. The paragraph above is traced for annual frequency and the actual-days type; not verified beyond that.
From the separate partial-month trace (not the annual path): a partial month is a whole month when partial periods are off, and the day fraction (15 of 30 = 0.5) when on; only the first and last period are fractional, interior periods stay whole. Rounding applies to the money at the currency scale, not to the count.
Help says month precision rounds a partial month to a whole one, but its own worked example
prorates a half month to 0.5; both hold under different partial-period settings (above). [Help: `ind.pricing_proration_variables.htm`]

## How pricing uses it

- Subscription element: unit price x quantity x pricing term count; Proration element emits the term count.
- [Platform behaviour, traced] In the shipped default procedure the term count is the Proration step's multiplier. The step reads the selling model's pricing term unit (not the line's own unit) as both the period and the term unit, and the line's `SubscriptionTerm` as the term; with no end date the end is start + term (in that unit) - 1 day. A line with dates only has the count derived from them. So send a term in the selling model's unit (48 on an Annual model is 48 periods; term illustrative) or dates. Place does not derive `SubscriptionTerm` from dates [Platform behaviour, traced]. The trace shows Place filling a missing term context tag with the selling model's pricing term when the line's selling model option is Term Defined, but not that fill reaching the saved line. In the measured requests (price book entry only, no `ProductSellingModelId` in the request; the saved line's selling model was Term Defined) the saved unit was `Annual` but `SubscriptionTerm` stayed null: a dates-only Term Defined Annual line (System pricing, configuration method Force, rules on) was priced from its dates alone (a whole-year term count) and came out higher by exactly the missing commitment-term step, because the term-keyed discount never ran. That step is one the measured org's customised pricing procedure adds when a header switch is on (it was on; not a shipped step). The result held both standalone and as a bundle component, against a line sent with `SubscriptionTerm` and unit `Annual` instead of an end date [Measured: 2026-11-11, 264, scratch]. Why the term was not filled was not established. So for pricing, dates suffice; send the term explicitly when anything reads `SubscriptionTerm` (such as a commitment-term discount filter, which skips such a line).
- A second dates-only create (configuration method not recorded) matched the saved fields above: `SubscriptionTerm` null, the unit filled, the term count from the dates [Measured: 2026-11-12, 264, scratch]. A dates-only PATCH on an existing line (one measurement; configuration method Skip, System pricing, a Term Defined Annual line created with a term) left `SubscriptionTerm` at its old value while the pricing term count and the total followed the new dates [Measured: 2026-11-12, 264, scratch]. Send the term again when the dates change if anything reads `SubscriptionTerm`. Details: `rlm-business-apis` (Other Place results).
- One-time and evergreen use the Pricing Setup default when set (see element file).
- How the policy and option values reach the element (via context tags) is not in Help; see the element file.

## Period examples (Help) [Help: `ind.pricing_*_proration_examples*.htm`]

Convention: periods are start-date to day-before-next-start; a part period counts days used / days in that period. Without partial proration each touched period counts 1.0.

| Period | Mode | Partial | Term count | Note |
|---|---|---|---|---|
| Annual, 2025-03-28 to 2026-02-04, $800 | Anniversary or DayOfPeriod | on / off | 314/365 = 0.860274 / 1.0 | $688.22 / $800 |
| Annual same dates | AlignToCalendar | on / off | 279/365 + 35/365 = 0.860274 / 2.0 | $688.22 / $1,600 |
| Monthly same dates, $90 | DayOfPeriod 5 | on / off | 8/31 + 10 = 10.258065 / 11.0 | $923.23 / $990 |
| Monthly same dates | AlignToCalendar | on / off | 4/31 + 10 + 4/28 = 10.271889 / 12.0 | $924.47 / $1,080 |
| Quarterly same dates, $200 | AlignToCalendar | on / off | Help: 3.436464 (3.427 by its own sum) / 5.0 | $687.29 / $1,000 |
| Semi-annual same dates, $400 | DayOfPeriod 5 | on / off | 130/181 + 1 = 1.718232 / Help: 3.0 (unreliable; 2.0 expected) | $687.29 / Help: $1,200 (unreliable) |
| Weekly, 75 days, $12.01 x 12 | any (1 = Monday ... 7 = Sunday) | n/a | 75/7 = 10.71 | Help: $1,543.36 |

Leap years: end-of-month anniversaries move to the latest valid day. Annual from 2024-02-29 to 2025-02-27 = 1.0. Annual 2027-02-28 to 2028-02-27 = 365/366 = 0.99726 ($997.27) because the full period expects 2028-02-28; to 2028-02-28 = 1.0. Monthly from the 30th/31st: Jan 30 to Feb 27 (29 days) then Feb 28 to Mar 29 = 2.0.

Worked example: $50/month product, subscribed on the 15th of a 30-day month: 15 days / 30 days = 0.5, so $50 x 0.5 = $25 for that month. [Help: `ind.pricing_proration_variables.htm`]

### <a name="measured-partial-year"></a>Measured: a partial year prorates by days

[Measured] A Term Defined annual line priced with the repo's `Default Proration Policy` (`qb-pcm`: Standard Time
Periods, remainder `AddToLast`, partial periods allowed):

| Line dates | `PricingTermCount` |
|---|---|
| 2026-04-01 to 2028-12-31 | 2.753424658 (2 + 275/365) |
| 2028-04-01 to 2029-12-31 | 1.7514 (1 + 275/366) |
| Dates covering whole years | a whole number (2 and 1 measured) |

Whole years count 1 each and the partial year counts by days, so 33 months is not 2.75 terms. Both values (dates illustrative; the rule is what was measured)
fit a partial period at the start of the line (April to December, 275 days) divided by the length of the calendar
year it falls in (365 in 2026, 366 in 2028); which period anchoring produces this wasn't isolated, so check dates
that cross a leap year against a live run. A source
that prorates by months remaining ÷ 12 differs by the day fraction: on a mid-term amendment or co-termed add the
line totals won't match it. Either accept the day-based value or state the source's value as the
expected result only where the dates cover whole years.

## Data and automation

Objects: `ProductSellingModel`, `ProrationPolicy`, `ProductSellingModelOption`. This repo loads them with the `qb-pcm` plan (policy keyed on `Name`; `ProrationPolicyId` on options is create-only on reload). Repo data rules: [`../sfdmu-data-plans/SKILL.md`](../sfdmu-data-plans/SKILL.md), [`../../../datasets/sfdmu/qb/en-US/qb-pcm/README.md`](../../../datasets/sfdmu/qb/en-US/qb-pcm/README.md). Object relationships: [`../revenue-cloud-data-model/domains/pricing.md`](../revenue-cloud-data-model/domains/pricing.md).

## Verify

```bash
sf data query --target-org <sf_alias> -q "SELECT Name, SellingModelType, PricingTerm, PricingTermUnit, Status FROM ProductSellingModel"
sf data query --target-org <sf_alias> -q "SELECT Name, ProrationPolicyType, RemainderStrategy, ArePartialPeriodsAllowed FROM ProrationPolicy"
sf data query --target-org <sf_alias> -q "SELECT Product2Id, ProductSellingModelId, ProrationPolicyId FROM ProductSellingModelOption WHERE Product2Id = '<id>'"
```
Then Simulate with Effective From/To and compare to the table above.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Policy cannot be assigned | Option uses a One Time model | Use term-defined or evergreen |
| Always a full period | Allow partial proration off, or no policy on the option | Tick it; assign policy |
| Evergreen/one-time price covers wrong periods | The procedure's term-count constants, or the Pricing Setup default term count | Check `EvergreenPricingTermCountConstant` / `OneTimePricingTermCountConstant` in the procedure; set Evergreen 1 on the Setup page (no API). Blanking One Time stops its proration per core (see step 2) |
| Day/month ignored | Start Proration Period not DayOfPeriod | Change mode |
| Cannot create policy | No term-defined/evergreen model or no price book entry | Create those first |

## Open questions

- Help's quarterly example prints 3.427 and 3.436464 for the same case ($687.29 uses the latter); the 3.427 arithmetic gives $685.48. The semi-annual no-partial example prints 3.0 / $1,200 next to what reads as a leftover drafting note; two touched periods give 2.0 / $800 (inferred). The same article's utilized range "28-Mar to 4-Apr (130 Days)" should read 4-Aug.
- Month precision: reconciled by the partial-month trace above (partial periods off: whole month; on: day fraction); not live-verified. Weekly arithmetic ($144.12 x 10.71 = about $1,543.5) does not reproduce $1,543.36. Treat these as illustrative.
- The monthly examples 5 and 6 repeat the annual case with $800 (a doc error, inferred).
- The context tags carrying policy values are not documented. (The Pricing Setup default term counts have no API at all; see [Default term counts](#default-term-counts).)
