# Price Revision (`PriceRevision`)

> Release 264 / API v68.0. Sources: `ind.pricing_use_the_price_revision_element_in_a_pricing_procedure.htm`,
> `ind.pricing_understand_price_revisions.htm`, `ind.pricing_apply_policy_driven_price_revisions.htm`,
> `ind.qocal_ramp_deal_compound_uplift.htm`, `ind.qocal_ramp_deal_compound_uplift_sales_reps.htm`,
> `ind.qocal_considerations_ramp_deals.htm`;
> shipped XML: `RLM_DefaultPricingProcedure` (two PriceRevision steps), PRM Disti and Recalc procedures;
> core 264 re-read for this pass (element parameter registration, compound grouping, error handling).

Adjusts a line's net unit price and subtotal by a percentage uplift: a policy-driven revision
(Flat, or Price Index/CPI from the Index Rate decision table), or a per-segment **compound ramp
uplift**. Policy and CPI data/verification: [`../../pricing-wiring/price-revision-cpi.md`](../../pricing-wiring/price-revision-cpi.md).
Ramp quote building: [`../../ramped-quotes/SKILL.md`](../../ramped-quotes/SKILL.md).
Policy, index-rate and region setup in any org: [`../../pricing-setup/price-revision-policies.md`](../../pricing-setup/price-revision-policies.md).

## When to use it
- Renewal uplifts from a Price Revision Policy (Flat manual value, or Price Index = CPI-driven). [Help]
- Compound (or standard) per-segment uplift on group ramp deals. [Help][Live, 2026-10-28]
- Not for discounts or list-price changes; use Volume Discount / Attribute Discount elements.
- Not supported for Partner/Customer Community users. [Help: `ind.pricing_apply_policy_driven_price_revisions.htm`]

## Configuration
| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Lookup table | `LookUpId`, `LookUpApiName`, `LookUpName` | literal | yes | Index Rate decision table; `LookUpId` is org-specific (`__LOOKUPID_INDEX_RATE_DECISION_TABLE__` placeholder in the Default and PRM procedures; a literal source-org id in Recalc). [Repo] |
| Valid Start Date (rule var) | `ValidStartDate` | input | yes | `ItemConsumerPriceIndexDate__std`; must fall in the IndexRate range. [Help][Repo] |
| Valid End Date | `ValidEndDate` | input | yes (repo) | same variable. [Repo] |
| Region (rule var) | `Region` | input | yes | `ItemPriceRevisionPolicyRegion__std`. [Help][Repo] |
| Quantity | `Quantity` | input (Numeric) | yes [Core] | `LineItemQuantity`. [Help][Repo] |
| Price Revision Policy | `PriceRevisionPolicy` | input (Text) | no [Core] | `ItemPriceRevisionPolicy__std` in repo (Help names `ItemPriceRevisionPolicyName_std`, one underscore). Blank policy with compound on and no formula = Flat default (see Runtime). [Help vs Repo] |
| Input Unit Price | `InputUnitPrice` | input (Currency) | yes [Core] | Help binds `ListPrice`; shipped XML binds `NetUnitPrice` (verified in all three procedures). [Help vs Repo] |
| Policy Type | `PolicyType` | input (Text) | yes unless compound [Core] | Flat or Price Index; `ItemPriceRevisionPolicyType__std`. [Help] |
| Price Revision Formula | `PriceRevisionFormula` | input | yes unless compound | `ItemPriceRevisionPolicyFormula__std`. [Help] |
| Policy Adjustment | `PolicyAdjustment` | input (Numeric) | no [Core] | `ItemUnitPriceUplift__std` (line `UnitPriceUplift`). [Repo] |
| Rate | `Rate` | output | yes | CPI rate, `ItemConsumerPriceIndex__std`. [Repo] |
| Applied uplift | `AppliedUnitPriceUplift` | output | compound ramp step only | `ItemApplUnitPriceUpliftPct__std`; only the Default `Uplift` step outputs it; the three CPI steps output Rate, NetUnitPrice and Subtotal. [Repo] |
| Net Unit Price / Subtotal | `NetUnitPrice`, `Subtotal` | output | yes | Revised price and total. [Repo] |
| Enable Compound Uplift | `IsCompoundUpliftEnabled` | literal | no | Visible only after a lookup table is chosen. [Help] |
| Ramp Identifier | `RampIdentifier` | input | compound | `ItemRampIdentifier`. [Help][Repo] |
| Base Price Multiplier | `PreviousSegmentMultiplier` | input (Percent) | compound | `ItemPreviousApplUnitPriceUpliftPct__std`. [Core] confirmed: this is the parameter behind the Builder label. It is a **percent** (38.6 means 38.6%, not 1.386); the engine seeds the multiplier as 1 + value/100, and 1 when blank. |
| Uplift Method | `UpliftMethod` | input | compound | `ItemRampUpliftType__std`. [Repo] |
| Effective From / To | `PriceRevisionEffectiveFrom`, `PriceRevisionEffectiveTo` | input | compound | `EffectiveFrom`, `EffectiveTo`. [Repo] |
| Other | `CurrencyIsoCode`, `HideWaterfall`, `IsRealTime` | | | Housekeeping. [Repo] |

[Core] Fixed parameters (element parameter registration): `Quantity` and `InputUnitPrice` (required),
`PriceRevisionPolicy` (optional), `PolicyType` / `PriceRevisionFormula` (required only when compound is
off), `PolicyAdjustment` (optional numeric). Shipped XML also carries `ValidStartDate`/`ValidEndDate`/`Region`
as lookup input columns; their requiredness comes from the lookup table, not this registration [inferred]. The five compound parameters (`RampIdentifier`, `PreviousSegmentMultiplier`, `UpliftMethod`,
`PriceRevisionEffectiveFrom/To`) exist only when `IsCompoundUpliftEnabled` is true; lookup columns add
dynamic input parameters. The Builder offers lookup, hide-waterfall and compound options for this element.

## Placement and ordering
- Runs after List Price (needs a base price) and before Proration/Subscription Price totals.
  Cross-element order: `../procedure-anatomy-and-ordering.md`.
- Repo places the renewal step under a ListGroup filtered to subscription lines without derived
  pricing, and the ramp step under a separate ListGroup for ramped amendments. [Repo]
- Help: "If the pricing procedure uses delta pricing and you enable Compound Uplift, the Price Revision element reprices every line in the ramp group each time it runs, regardless of the delta pricing setting. This behavior applies only to lines that use Compound Uplift. Delta pricing behaves normally for lines that do not use it." [Help: `ind.pricing_use_the_price_revision_element_in_a_pricing_procedure`]
- Delta skipping applies when the setting is on and the save is a PATCH edit with System pricing, Dual Persistence mode off, a completed calculation status (Completed with Pricing or with Tax) and no validation errors [Platform behaviour, traced]; further conditions (pricing permissions, the transaction's update tracking) also apply, so treat this list as partial (see [`../runtime-and-observability.md`](../runtime-and-observability.md)). If any of those does not hold, every line reruns and the uplift is applied again to untouched lines [Platform behaviour, traced]. With the setting on (read from the org), a System PATCH of one ramp line with no field change (configuration Skip) left every line's waterfall id unchanged (no new waterfall was saved), yet re-applied the compound uplift to every uplifted line's `NetUnitPrice`, unrounded, with totals unchanged [Measured: 2026-11-12, 264, scratch; one org]. Help's rule fits which lines moved, but not the unchanged waterfalls or the uplift compounding on the stored net; that path is not traced. Finish ramp edits with Reprice All and re-read every segment.

## Rules and limits
- Policy types: **Flat** (manual uplift value, no decision table) and **Price Index** (rate from
  the Index Rate decision table). Formula example `MAX(10, PriceIndex + 5)`; numbers are percents. [Help]
- Effective date ranges for the same region can't overlap (except multi-currency orgs), on both
  policies and index rates. [Help]
- Add Region picklist values on IndexRate before creating policies/rates. [Help]
- Winter '26+ orgs may have the Index Rate decision table deactivated; activate it in Setup ->
  Decision Tables. Refresh it if the waterfall looks wrong. [Help] See `../../decision-tables/SKILL.md`.
- CPI-tied renewal uplifts are not supported on ramped products, and CPI can't be combined
  with compound uplift.
  [Help: `ind.qocal_considerations_ramp_deals.htm`] Core enforces only the Price Index case (non-Flat
  `PolicyType` leaves the compound path); usage-based and derived-pricing exclusions are Help-only
  [Help]. Help also says usage-based and derived-pricing products don't support price uplifts, and CPI
  renewal uplifts apply only to termed assets [Help: `ind.qocal_consumer_price_index_and_uplifts_important_considerations.htm`].
   Measured ramp alternatives:
  [`../../pricing-wiring/price-revision-cpi.md`](../../pricing-wiring/price-revision-cpi.md).
- Enable Compound Uplift on a transaction without ramp segments falls back to standard
  calculation. Compound lines and standard lines can mix; standard ones don't compound. [Help]
- Changing/removing the lookup table auto-clears `IsCompoundUpliftEnabled`. [Help]
- With compound enabled, Policy Type and Formula no longer need values. [Help]

## Runtime behavior [Core]
- A line takes the compound path only when `UpliftMethod` equals `Compound` (case-insensitive),
  `PolicyType` is blank or Flat (a Price Index line is always standard), quantity is not negative or
  unparsable, and `RampIdentifier` is non-blank (blank = standard). A compound-intended line with a
  negative quantity is skipped, not priced. A line with no `InputUnitPrice` value is skipped silently.
- Standard path: the formula is evaluated with `PriceIndex` (the lookup's `Rate`) and `PolicyAdjustment`
  as variables, as a percent: net = input unit price x (1 + result/100). If the lookup returns no row
  (or the lookup call carried errors), `PriceIndex` defaults to 0 inside this step, so a Price Index
  policy with no matching Index Rate row yields a 0 index rather than a step failure: the formula still
  runs (`MAX(10, PriceIndex + 5)` gives 10) and this step logs no "rate not found" error. Whether the
  lookup layer itself logs one was not found: [inferred] none. The Index Rate lookup runs only when at
  least one line has a `PolicyType` value that is not Flat (case-insensitive; an empty string counts as
  not Flat); an all-Flat or all-null step skips it. A formula that evaluates to nothing logs `INVALID_PRICE_REVISION_FORMULA`
  ("Enter a valid Price Revision Formula and try again.") on the line. Any other exception in the
  standard path is thrown as an internal error carrying the exception text; whether that fails only the
  line or the whole pricing call was not determined [inferred: whole call]. [Core]
- Compound lines group by `RampIdentifier`. Per group: sort by Effective From; a missing date fails
  every segment with `MISSING_RAMP_SEGMENT_START_DATE` ("Compound ramp uplift requires an effective
  start date on every segment. One or more segments in this ramp group are missing a start date."), a
  duplicate with `DUPLICATE_RAMP_SEGMENT_START_DATE` ("Compound ramp uplift requires a unique effective
  start date for each segment. Two or more segments in this ramp group share the same start date."):
  whole group, nothing priced. Dates compare as UTC calendar days, so two segments on the same day
  with different times count as duplicates. The running multiplier is seeded once, from the first
  (earliest) segment's `PreviousSegmentMultiplier`.
- Math per segment: `mult(n) = mult(n-1) x (1 + uplift%(n)/100)`; applied% = (mult - 1) x 100;
  net = input unit price x mult. Uplift% comes from `PolicyAdjustment` (null = 0). Groups run in
  parallel when the procedure has at least 4 compound ramp groups, else sequentially (verified in core:
  the threshold is 4; segments within a group always run in order). An exception while pricing a
  segment logs `INVALID_PRICE_REVISION_FORMULA` on that segment and stops the group; earlier segments
  keep their outputs, later ones are not priced. Compound lines also write the applied uplift to
  `PriceRevisionValue` and `AppliedUnitPriceUplift`; the Index Rate lookup result (`Rate`) is not used.
- "Compound enabled" is detected by the presence of the `UpliftMethod` parameter on the step. Standard
  path with compound enabled, `PriceRevisionPolicy` blank and no formula: treated as Flat using
  `PolicyAdjustment` (net = input x (1 + adj/100), null = 0). A blank policy with a formula present, or
  a populated policy with no formula, goes through the formula path. With compound off and no formula,
  core's own comment says the evaluator surfaces `INVALID_PRICE_REVISION_FORMULA`; not run live [inferred].

## <a name="compound-ramp-uplift"></a>Compound ramp uplift

Each ramp segment's price uplifts on the *prior segment's* factor. The five prerequisites, the
ramp-path bindings, how the tracked default compares with the 264 template, the arithmetic and
what can't compound are in [`price-revision-compound-uplift.md`](price-revision-compound-uplift.md).

## Metadata shape
Elided skeleton; full parameter set in the Configuration table. Literal vs Parameter via `<type>`. [Repo]
```xml
<steps>
  <actionType>PriceRevision</actionType>
  <customElement>
    <parameters><input>true</input><name>RampIdentifier</name><output>false</output><type>Parameter</type><value>ItemRampIdentifier</value></parameters>
    <parameters><input>true</input><name>UpliftMethod</name><output>false</output><type>Parameter</type><value>ItemRampUpliftType__std</value></parameters>
    <parameters><input>true</input><name>IsCompoundUpliftEnabled</name><output>false</output><type>Literal</type><value>true</value></parameters>
    <parameters><input>true</input><name>LookUpId</name><output>false</output><type>Literal</type><value>__LOOKUPID_INDEX_RATE_DECISION_TABLE__</value></parameters>
    <parameters><input>true</input><name>LookUpApiName</name><output>false</output><type>Literal</type><value>Index_Rate_Decision_Table</value></parameters>
    <!-- Rate -> ItemConsumerPriceIndex__std; AppliedUnitPriceUplift -> ItemApplUnitPriceUpliftPct__std;
         PolicyAdjustment <- ItemUnitPriceUplift__std; NetUnitPrice, Subtotal outputs -->
  </customElement>
  <name>Uplift</name>
  <parentStep>Applyupliftstorampedsubscriptionsitemsduringamendment</parentStep>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
```
`LookUpId` differs per org (a real ID in raw retrieves); Default and PRM use the placeholder swapped at deploy, Recalc a literal id.

## Shipped in this repo (snapshot)
| Procedure | Step (actionType) | Parent group, seq | What it does |
|---|---|---|---|
| `RLM_DefaultPricingProcedure` | `AdjustNetUnitPriceandSubtotalbyusingpricerevision` (`PriceRevision`) | `Applypricerevisionforlineswithsubscriptionandwithoutderivedpricing`, 2 | Renewal policy revision (Flat/PriceIndex) |
| same | `Uplift` (`PriceRevision`) | `Applyupliftstorampedsubscriptionsitemsduringamendment`, 2 | Ramp-path compound/standard uplift |
| `RLM_PRM_DISTI_Pricing_Procedure`, `RLM_Revenue_Management_Recalc_Procedure` | `AdjustNetUnitPriceandSubtotalbyusingpricerevision` (`PriceRevision`) | same parent as the default, 2 | Renewal policy revision, as in the default (Recalc carries a literal `LookUpId`, not the placeholder) |
| same | `Uplift` (`FormulaBasedPricing`) | `Applyupliftstorampedsubscriptionsitemsduringamendment`, 2 | Legacy ramp uplift: no `IsCompoundUpliftEnabled`, so no compound ramp uplift in these procedures |

`RLM_Price_Distribution_Procedure` has no Price Revision step. [Repo, checked against the XML]

Snapshot. Discover: `python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify
- Builder Simulate with Index Rate in range; price waterfall shows a Price Revision entry. [Help]
- Compounding: segment breakdown query (below), checked against the math in *Runtime behavior*.

### Inspect / research (read-only)
```bash
# 0. Discover the org's ACTIVE pricing procedure first; RLM_DefaultPricingProcedure is the
#    template default, but an org may run a different one. Never assume the name.
#    --versions is REQUIRED to mark the active version ([ACTIVE]); without it the tool
#    prints set names only and can't tell active from draft.
python scripts/expression_sets/list_expression_sets.py --target-org <sf_alias> \
    --type PricingProcedure --versions
# Is compound enabled, and what feeds the rate? Inspect the SELECTED procedure for a ramp-path
# PriceRevision BKM (the ramp branch is "Applyupliftstoramped...") and read IsCompoundUpliftEnabled
# + its Rate input. The tracked RLM_DefaultPricingProcedure ships one there
# (IsCompoundUpliftEnabled=true); an ABSENT ramp-path PriceRevision is the signal that compound
# uplift is not configured on that procedure (e.g. a custom procedure that predates the migration).
python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> \
    --developer-name <PRICING_PROCEDURE> --params

# Do live compound ramps exist? (any Compound row = yes)
sf data query --target-org <sf_alias> -q \
  "SELECT RampUpliftType, COUNT(Id) FROM QuoteLineGroup GROUP BY RampUpliftType"

# Segment breakdown for one quote (verify the compounding numerically):
sf data query --target-org <sf_alias> -q "SELECT SegmentName, IsPrimarySegment, \
  StartDate, EndDate, UnitPrice, NetUnitPrice, UnitPriceUplift, \
  ApplUnitPriceUpliftPct, RampUpliftType FROM QuoteLineItem \
  WHERE QuoteId='<id>' AND RampUpliftType='Compound' ORDER BY StartDate NULLS FIRST"
```
Diff the ramp path org-vs-org with `diff_expression_set.py`. Building the compound-capable ramp
quote (a **group** ramp via `placeSalesTransaction` create -> `groupRampAction: EditGroup` ->
clone, then per-segment `UnitPriceUplift` + `RampUpliftType='Compound'` on the group) is a
transaction-building task: see [`../../ramped-quotes/SKILL.md`](../../ramped-quotes/SKILL.md) (API, or
the quote UI in `ui-group-ramp.md`). Do **not** use the line-level `createRampDeal` or the legacy
`/commerce/.../ramp-deals` API; neither produces the group that holds the compound uplift mode.
Help snapshots: `ind.qocal_ramp_deal_compound_uplift.htm`,
`ind.qocal_ramp_deal_compound_uplift_sales_reps.htm`,
`ind.pricing_use_the_price_revision_element_in_a_pricing_procedure.htm`.

## Troubleshooting
| Symptom / error | Cause | Fix |
|---|---|---|
| Compound selected but price is standard | Uplift Method blank, `RampIdentifier` blank, or non-Flat `PolicyType` | Bind `UpliftMethod` to `ItemRampUpliftType__std`; set the ramp id [Help][Core] |
| `MISSING_RAMP_SEGMENT_START_DATE` / `DUPLICATE_RAMP_SEGMENT_START_DATE` on every segment | A segment missing or duplicating Effective From (same UTC day counts) | Unique Effective From per segment [Core][Help] |
| `INVALID_PRICE_REVISION_FORMULA` ("Enter a valid Price Revision Formula and try again.") | Policy formula empty/non-numeric, or compound segment threw | Fix the policy record's formula [Core] |
| Compound option absent in picklist | Advanced Detail Line Pricing off | Turn on; never turn off with live compound data [Repo] |
| Compound checkbox missing in Builder | No lookup table selected | Select Index Rate table first [Help] |
| Year-2 amendment double-uplifts | Ramp filter lost the group gate | Keep `IsLineGroupRamped__std = true` [Repo] |
| No CPI revision / zero rate | Index Rate DT inactive/stale, region or date out of range | Activate and refresh DT; check IndexRate ranges [Help] |
| Overlap error on policy/rate | Same-region date overlap | Fix ranges (single currency) [Help] |
| Ungrouped segments never compound | Line-level `createRampDeal` | Build a group ramp |

## Notes
- Error message text above is the English text; it is localized per user language [Core].
- Generic lifecycle: `../../expression-sets/SKILL.md`.

## Resolved disagreements
| Point | Help | Repo | Core | Winner |
|---|---|---|---|---|
| Base Price Multiplier name | label only | `PreviousSegmentMultiplier` | same, Percent type | Core confirms repo |
| `ListPrice` vs `NetUnitPrice` as input | `ListPrice` | `NetUnitPrice` | parameter is `InputUnitPrice`; bound tag free | Bind what the step should uplift; repo's `NetUnitPrice` is the post-discount price |
| Policy tag `..PolicyName_std` vs `ItemPriceRevisionPolicy__std` | name tag | policy tag | parameter `PriceRevisionPolicy`; tag free | Match your context definition |
| Percent units | | `applied%` in percent, measured live | Percent type, /100 | Agree |
