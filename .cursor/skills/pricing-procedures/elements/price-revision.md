# Price Revision (`PriceRevision`)

> Release 264 / API v68.0. Sources: `ind.pricing_use_the_price_revision_element_in_a_pricing_procedure.htm`,
> `ind.pricing_understand_price_revisions.htm`, `ind.pricing_apply_policy_driven_price_revisions.htm`,
> `ind.qocal_ramp_deal_compound_uplift.htm`, `ind.qocal_ramp_deal_compound_uplift_sales_reps.htm`,
> `ind.qocal_considerations_ramp_deals.htm`;
> shipped XML: `RLM_DefaultPricingProcedure` (two PriceRevision steps), PRM Disti and Recalc procedures;
> verified against core 264 (formal parameters, compound grouping, error keys).

Adjusts a line's net unit price and subtotal by a percentage uplift: a policy-driven revision
(Flat, or Price Index/CPI from the Index Rate decision table), or a per-segment **compound ramp
uplift**. Policy and CPI data/verification: [`../../pricing-wiring/price-revision-cpi.md`](../../pricing-wiring/price-revision-cpi.md).
Ramp quote building: [`../../ramped-quotes/SKILL.md`](../../ramped-quotes/SKILL.md).

## When to use it
- Renewal uplifts from a Price Revision Policy (Flat manual value, or Price Index = CPI-driven). [Help]
- Compound (or standard) per-segment uplift on group ramp deals. [Help][Repo, live-verified 2026-10-28]
- Not for discounts or list-price changes; use Volume Discount / Attribute Discount elements.
- Not supported for Partner/Customer Community users. [Help: `ind.pricing_apply_policy_driven_price_revisions.htm`]

## Configuration
| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Lookup table | `LookUpId`, `LookUpApiName`, `LookUpName` | literal | yes | Index Rate decision table; `LookUpId` is org-specific (`__LOOKUPID_INDEX_RATE_DECISION_TABLE__` placeholder in repo). [Repo] |
| Valid Start Date (rule var) | `ValidStartDate` | input | yes | `ItemConsumerPriceIndexDate__std`; must fall in the IndexRate range. [Help][Repo] |
| Valid End Date | `ValidEndDate` | input | yes (repo) | same variable. [Repo] |
| Region (rule var) | `Region` | input | yes | `ItemPriceRevisionPolicyRegion__std`. [Help][Repo] |
| Quantity | `Quantity` | input | yes | `LineItemQuantity`. |
| Price Revision Policy | `PriceRevisionPolicy` | input | yes | `ItemPriceRevisionPolicy__std` in repo (Help names `..PolicyName_std`). [Help vs Repo] |
| Input Unit Price | `InputUnitPrice` | input | yes | Help: `ListPrice`; repo: `NetUnitPrice`. |
| Policy Type | `PolicyType` | input (Text) | yes unless compound [Core] | Flat or Price Index; `ItemPriceRevisionPolicyType__std`. [Help] |
| Price Revision Formula | `PriceRevisionFormula` | input | yes unless compound | `ItemPriceRevisionPolicyFormula__std`. [Help] |
| Policy Adjustment | `PolicyAdjustment` | input | no | `ItemUnitPriceUplift__std` (line `UnitPriceUplift`). [Repo] |
| Rate | `Rate` | output | yes | CPI rate, `ItemConsumerPriceIndex__std`. [Repo] |
| Applied uplift | `AppliedUnitPriceUplift` | output | yes | `ItemApplUnitPriceUpliftPct__std`. [Repo] |
| Net Unit Price / Subtotal | `NetUnitPrice`, `Subtotal` | output | yes | Revised price and total. [Repo] |
| Enable Compound Uplift | `IsCompoundUpliftEnabled` | literal | no | Visible only after a lookup table is chosen. [Help] |
| Ramp Identifier | `RampIdentifier` | input | compound | `ItemRampIdentifier`. [Help][Repo] |
| Base Price Multiplier | `PreviousSegmentMultiplier` | input (Percent) | compound | `ItemPreviousApplUnitPriceUpliftPct__std`. [Core] confirmed: this is the parameter behind the Builder label. It is a **percent** (38.6 means 38.6%, not 1.386); the engine seeds the multiplier as 1 + value/100, and 1 when blank. |
| Uplift Method | `UpliftMethod` | input | compound | `ItemRampUpliftType__std`. [Repo] |
| Effective From / To | `PriceRevisionEffectiveFrom`, `PriceRevisionEffectiveTo` | input | compound | `EffectiveFrom`, `EffectiveTo`. [Repo] |
| Other | `CurrencyIsoCode`, `HideWaterfall`, `IsRealTime` | | | Housekeeping. [Repo] |

[Core] Fixed parameters: `Quantity` and `InputUnitPrice` (required), `PriceRevisionPolicy` (optional),
`PolicyType` / `PriceRevisionFormula` (required only when compound is off), `PolicyAdjustment` (optional
numeric). The five compound parameters (`RampIdentifier`, `PreviousSegmentMultiplier`, `UpliftMethod`,
`PriceRevisionEffectiveFrom/To`) exist only when `IsCompoundUpliftEnabled` is true; lookup columns add
dynamic input parameters. The Builder offers lookup, hide-waterfall and compound options for this element.

## Placement and ordering
- Runs after List Price (needs a base price) and before Proration/Subscription Price totals.
  Cross-element order: `../procedure-anatomy-and-ordering.md`.
- Repo places the renewal step under a ListGroup filtered to subscription lines without derived
  pricing, and the ramp step under a separate ListGroup for ramped amendments. [Repo]
- With delta pricing + compound uplift, every line in the ramp group reprices on each run
  regardless of the delta setting; non-compound lines are unaffected. [Help]

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
  [Help: `ind.qocal_considerations_ramp_deals.htm`] Measured ramp alternatives:
  [`../../pricing-wiring/price-revision-cpi.md`](../../pricing-wiring/price-revision-cpi.md).
- Enable Compound Uplift on a transaction without ramp segments falls back to standard
  calculation. Compound lines and standard lines can mix; standard ones don't compound. [Help]
- Changing/removing the lookup table auto-clears `IsCompoundUpliftEnabled`. [Help]
- With compound enabled, Policy Type and Formula no longer need values. [Help]

## Runtime behavior [Core]
- A line takes the compound path only when `UpliftMethod` equals `Compound` (case-insensitive) with
  a valid quantity; anything else, including blank, is standard. A compound-intended line with a
  negative quantity is skipped, not priced.
- Compound lines group by `RampIdentifier`. Per group: sort by Effective From; a missing date fails
  every segment with `MISSING_RAMP_SEGMENT_START_DATE`, a duplicate with
  `DUPLICATE_RAMP_SEGMENT_START_DATE` (whole group, nothing priced).
- Math per segment: `mult(n) = mult(n-1) x (1 + uplift%(n)/100)`; applied% = (mult - 1) x 100;
  net = input unit price x mult. Uplift% comes from `PolicyAdjustment` (null = 0). Groups run in
  parallel when 4 or more groups exist in one step, else sequentially.
- Standard path with compound enabled and no policy and no formula: treated as Flat using
  `PolicyAdjustment`. With compound off, a missing formula yields `INVALID_PRICE_REVISION_FORMULA`.

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
`LookUpId` differs per org (a real ID in raw retrieves); the repo uses the placeholder swapped at deploy.

## Shipped in this repo (snapshot)
| Procedure | Step | What it does |
|---|---|---|
| `RLM_DefaultPricingProcedure` | `AdjustNetUnitPriceandSubtotalbyusingpricerevision` | Renewal policy revision (Flat/PriceIndex) |
| same | `Uplift` | Ramp-path compound/standard uplift |
| `RLM_PRM_DISTI_Pricing_Procedure`, `RLM_Revenue_Management_Recalc_Procedure` | PriceRevision steps | Same pattern |
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
| Compound selected but price is standard | Uplift Method blank | Bind `UpliftMethod` to `ItemRampUpliftType__std` [Help] |
| Whole ramp group fails pricing | A segment missing or duplicating Effective From | Unique Effective From per segment [Help] |
| Compound option absent in picklist | Advanced Detail Line Pricing off | Turn on; never turn off with live compound data [Repo] |
| Compound checkbox missing in Builder | No lookup table selected | Select Index Rate table first [Help] |
| Year-2 amendment double-uplifts | Ramp filter lost the group gate | Keep `IsLineGroupRamped__std = true` [Repo] |
| No CPI revision / zero rate | Index Rate DT inactive/stale, region or date out of range | Activate and refresh DT; check IndexRate ranges [Help] |
| Overlap error on policy/rate | Same-region date overlap | Fix ranges (single currency) [Help] |
| Ungrouped segments never compound | Line-level `createRampDeal` | Build a group ramp |

## Open questions
- Exact message text is a localized label; keys are listed in Runtime behavior.
- Generic lifecycle: `../../expression-sets/SKILL.md`.

## Resolved disagreements
| Point | Help | Repo | Core | Winner |
|---|---|---|---|---|
| Base Price Multiplier name | label only | `PreviousSegmentMultiplier` | same, Percent type | Core confirms repo |
| `ListPrice` vs `NetUnitPrice` as input | `ListPrice` | `NetUnitPrice` | parameter is `InputUnitPrice`; bound tag free | Bind what the step should uplift; repo's `NetUnitPrice` is the post-discount price |
| Policy tag `..PolicyName_std` vs `ItemPriceRevisionPolicy__std` | name tag | policy tag | parameter `PriceRevisionPolicy`; tag free | Match your context definition |
| Percent units | | `applied%` in percent, live-verified | Percent type, /100 | Agree |
