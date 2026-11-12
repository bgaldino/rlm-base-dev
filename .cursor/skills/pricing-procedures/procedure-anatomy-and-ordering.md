# Pricing Procedure Anatomy and Element Ordering

> Release 264 / API v68.0. Sources: `ind.pricing_configure_pricing_procedure.htm`,
> `ind.pricing_understand_pricing_elements.htm`, `ind.pricing_add_aggregate_price_element.htm`,
> `ind.pricing_use_the_aggregate_price_element.htm`; shipped XML
> `RLM_DefaultPricingProcedure`; live findings recorded by the repo owner.

This file owns the **cross-element** rules: how a pricing procedure is shaped, which
order elements must run in, and why. Each element file in `elements/` keeps only its
own local placement notes and links back here.

## How a pricing procedure is shaped

- **Header record, then elements.** A pricing procedure is an Expression Set with
  `interfaceSourceType: PricingProcedure` and process type `DefaultPricing` ("Pricing" in
  the UI; `processType` in Metadata API XML, `usageType` in Connect) [Repo], plus a **usage subtype** (Revenue Cloud, Commerce, Insurance, …) and a
  **context definition** (`SalesTransactionContext` or an extension of it) [Help].
  Element lookups offer only the decision tables from pricing recipes assigned to that
  subtype [Help]. You can change the subtype when you clone a procedure, not when you
  edit it [Help].
- **Each element is one step.** Elements read and write **context tags** (for example
  `ListPrice`, `NetUnitPrice`, `ItemNetTotalPrice`). Variables are mapped to tags, and
  the tags carry values from one element to the next [Help].
- **Scope comes from placement and tags.** An element at the top level runs for every line
  unless a List Group filter narrows it; whether a result is per line or per header depends on
  the context node of the tags it reads and writes, not on placement [Core]. An element inside a **List Group** runs only on the lines that the
  group's **List Operation** (`AdvancedListFilter`) lets through. In metadata both are
  flat `<steps>` entries: a child names its group in `parentStep`, and `sequenceNumber`
  restarts at 1 under each parent [Repo]. See
  [`elements/list-group-and-list-operation.md`](elements/list-group-and-list-operation.md).
- **Branching uses mutually exclusive lanes.** Contract pricing, derived pricing,
  last-transaction pricing and the plain path are separate List Groups whose filters
  exclude each other (for example "without derived or last-transaction pricing"). A
  line that matches two lanes is priced twice [Repo, inferred]. Moving a line between lanes
  means changing both lanes' filters together; the measured example routes positive amendment
  adds from the last-transaction lane to the new-sale lane, in
  [`elements/volume-and-tier-discount.md`](elements/volume-and-tier-discount.md) → Re-banding
  positive amendment adds.
- **Versions and rank.** At run time the engine ignores disabled versions, keeps the
  enabled versions whose start/end dates cover the execution date, and uses the one with
  the **greatest rank** (strictly greater, so on a tie the version listed first stays; a
  version with no rank loses to any ranked one) [Core]. Same rule Help states for
  discovery procedures [Help]. A caller that names a version number or id gets that version
  if its dates match, regardless of rank [Core]. Details:
  [operations-and-troubleshooting.md](./operations-and-troubleshooting.md) section 2.
- **Include in Output.** At least one element must have *Include in Output* selected,
  or the procedure returns nothing for downstream processing [Help].
- **Local list variables** hold a value that one element calculates so a later element
  can reuse it, without a context tag. The element that writes the variable must come
  **before** the element that reads it, or the read resolves to null. They can't be
  passed in from outside, and Map Line Item and Price Propagation can't use them [Help].

## The phase order the shipped default follows (snapshot)

`RLM_DefaultPricingProcedure` has 42 top-level steps. Grouped into phases, they run in
this order (numbers in parentheses are top-level `sequenceNumber`s; the version has 109 steps in all, Draft, rank 1). This is a snapshot that will age; print the live tree with
`python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name>`.

| # | Phase | Elements (actionType) | Why here |
|---|---|---|---|
| 1 | Set up | Pricing Setting (`PricingSettings`) | Maps the standard pricing variables. Always first |
| 2 | Detail lines | Map Line Item (`BreakdownLineMapping`) | Maps item → item detail. Put it right after Pricing Setting |
| 3 | Inputs | Assignment (3), default-contract List Group (4) | Passes the pricing contract to lines before any lookup reads it |
| 4 | Base price | List Price (`ListPrice`) from the price book and the cost book (5-6) | Fills `ListPrice` and unit cost |
| 5 | Dates and contract list price | Assignment of the pricing date (7), then List Groups (8-12) | Pricing date and contract list price/net price for contract lines |
| 6 | Choose a lane | List Groups (13-16): input unit price for contract and plain lines (13-14), item net total (15), clear the contract-applied unit price (16); last-transaction lines are handled later (26-27) | Sets `InputUnitPrice` → `NetUnitPrice` once per line |
| 7 | Adjustments | Attribute (`AttributeDiscount`, 17-18), Bundle (`BundleDiscount`, 19), Volume (`VolumeDiscount`, 20-21), Manual (`ManualDiscount`, 22), amount/percentage discounts (23) | Each one discounts the running `NetUnitPrice` |
| 8 | Revisions | Price Revision (`PriceRevision`, 24-25): non-ramp and ramp uplift on amendment | Uplift or CPI on top of the discounted price |
| 9 | Last-transaction lines | List Groups (26-27) | Net unit price and net total for contracted/last-transaction lines |
| 10 | Term pricing | Proration (`Proration`) and Subscription Price (`SubscriptionPricing`), List Groups 28-33 | Turns the unit price into a term amount |
| 11 | Line totals | Formula-Based Pricing (`FormulaBasedPricing`) cost/margin (34), Assignment of totals (35) | Line-level formulas run **before** the closing block |
| 12 | Header inputs | List Groups (36-38): amount/percentage header discount, header price override | Sets header values for DDS to distribute |
| 13 | Distribute | Discount Distribution Service (`DiscountDistributionService`, 39) | Rewrites line `NetUnitPrice` / `ItemNetTotalPrice` |
| 14 | Roll up | Aggregate Price (`GroupingAndAggregatePricing`, 40-42) | `TotalAmount`, `Subtotal`, `ItemGroupSummarySubtotal` |

Phases 13–14 (plus Rounding Values when present) make up the **closing block**, the
fixed final section of the procedure. The rules below are about that block.

## Save-time procedure rules core enforces

Each is a save-time error, so the version cannot be saved or activated, with the quoted
text [Core]. Counts are over all steps, including those inside List Groups.

| Rule | Error text (abridged) |
|---|---|
| Pricing Setting must exist and be first: any other step (Commerce excepted) ordered before the first Pricing Setting is rejected too; only one allowed | `Add Pricing Setting as the first element in the pricing procedure.` / `You can only add one Pricing Setting element in a pricing procedure.` |
| Step names unique | `Each step must have a unique name. The following step names are used more than once: {0}` |
| One Discount Distribution Service (DDS) | `You can use only one Discount Distribution Service element in a pricing procedure.` |
| After DDS only Aggregate or Rounding Values steps (Rule 1) | `You can add the Discount Distribution Service element only before the Rounding Rules and Aggregate elements or you can make it the only element in a pricing procedure.` |
| DDS needs a valid participating condition or lookup | `Add a valid participating condition or delete the condition in the Discount Distribution Service element.` |
| DDS and Derived Price never together | `You can’t have the Derived Price and Discount Distribution Service elements in the same pricing procedure. Delete one of them and try again.` |
| Promotion Execution and Derived Price never together | `You can’t have the Derived Price and Promotion Execution elements in the same pricing procedure. Delete one of them and try again.` (Advanced Promotion Execution has the same pairing error, and only Assignment, Formula, Aggregation or List Group steps may follow it; `GPMPromotionExecution` is not part of this rule) |
| One Derived Price; needs *Is Derived* mapped in Pricing Setting | `You can only have one derived price element in a procedure.` / `Map the Is Derived variable to a value in the Pricing Settings element if you want to add a Derived Pricing element to your procedure.` |
| One Pricing Propagation, not inside a List Group, kept in sync with *Enable Propagation* in Pricing Setting, and not with Derived Price, Promotion Execution or Map Line Item (`GPMPromotionExecution` does not count; Advanced is checked only for the Communications subtype) | `Only one Pricing Propagation element is allowed in the pricing procedure…` / `Pricing Propagation element is not allowed in List Container element…` / `You must add Pricing Propagation element when propagation is enabled…` / `You must select Enable Propagation in the Pricing Settings element when the Pricing Propagation element is added.` / `Pricing Propagation element is not allowed with incompatible elements…` |
| Commerce pricing element (`CommercePricing`) stands alone | `You can only add the Commerce element to this pricing procedure.` |
| Element count per procedure (org value, max 200) | `The limit of {0} pricing elements that can be added to the {1} pricing procedure was reached in the org. Delete a pricing element and try again.` |
| Procedure count per org (max 10000) | `The limit of {0} pricing procedures in the org was reached. Delete a pricing procedure and try again.` |
| Promotion Execution rule library must exist, share the procedure's context definition and be a promotions library | `The <rule library> {0} used in the pricing procedure either doesn’t exist, its context definition isn't the same as the pricing procedure's context definition, or its usage type isn’t Global Promotions Management.` (a Line-only scope applies to the RLM promotions library) |
| Context definition for the Communications (CME) usage subtype | `We couldn't save the pricing procedure. Set the Context Definition to ConsumerSalesContext or one of its extensions, and try again.` (not the Revenue Cloud subtype) |

If the procedure is only a DDS (optionally followed by Aggregate/Rounding steps), or is a
lone Commerce step, core skips the Pricing Setting check [Core]. Other checks (lookup table valid
for the subtype's recipes, variable names, etc.) are per element: see the element files.

**Builder-only order checks** [Core]: the Builder also checks top-level order before saving, but
no server-side equivalent was found, so a Metadata API or Connect save is not stopped by them.
Map Line Item must be the second top-level element (`The Map Line Item must be the second element
in your pricing procedure.`, same text in a discovery procedure); a Commerce Pricing element must
be the only one (`You can only add one Commerce Pricing element to this pricing procedure.` for two).
Keep XML and overlays in that order anyway: Help documents the same positions.

## Rule 1: in a procedure with DDS, only Aggregate Price or Rounding Values after it

The closing block is Discount Distribution Service (`DiscountDistributionService`), the
`GroupingAndAggregatePricing` aggregate steps, and Rounding Rules. Core's check is
relative to DDS: every step ordered **after** the DDS step must be
`GroupingAndAggregatePricing` or `RoundingValues`, so a `FormulaBasedPricing` (or any
other) step after DDS is rejected. The check only runs when the procedure has a DDS
[Core]; the shipped PRM and Recalc procedures have none and end with an Assignment
after their aggregates [Repo]. Everything below assumes a procedure with DDS, like the
default. The error message is **misleading**: it names DDS, not your formula step
[Live, repo owner]:

```
INVALID_INPUT: You can add the Discount Distribution Service element only
before the Rounding Rules and Aggregate elements …
```

The real cause is ordering. In a procedure with DDS, a top-level formula over header tags that
depends on aggregate outputs can't sit after DDS. This has two consequences for an overlay that adds
a formula computed *from* aggregate results:

- Place new `GroupingAndAggregatePricing` steps with `afterStep` anchored to the
  **last existing aggregate**. They slot into the aggregate band cleanly.
- A `FormulaBasedPricing` step that uses those aggregate outputs has **no position
  that is both accepted and fed fresh values**. You *can* add a top-level formula over header tags: a
  top-level (no `parentStep`) `FormulaBasedPricing` step placed **before** the closing
  block is accepted, and it does write to the record. This was proven live with a
  `TotalMarginAmount__c / TotalAmount → TotalMarginPercent__c` step placed just before
  DDS. But **before** the aggregates, its inputs still hold the values **loaded from
  the record at the start of the reprice**, which are the *previous* reprice's
  numbers. So the formula lags one full reprice: it looks about right on an unchanged
  quote and is visibly wrong after any change. **After** the aggregates, where the
  inputs are fresh, the rule rejects the step. Calculate that value another way: an
  extra aggregate or calculation step earlier in the graph, or a Salesforce formula
  field on the record.

## Rule 2: aggregates stay after DDS

Moving the aggregates (and the formula) higher doesn't work. The aggregate band is
pinned *after* DDS by a real data dependency, not just by convention: DDS **rewrites**
the per-line `NetUnitPrice` / `ItemNetTotalPrice` that `TotalAmount` sums. Moving the
SUM above DDS would sum prices from *before* the header discount, which gives the
wrong total. Moving them doesn't free a slot for the formula either: the boundary is
the DDS step, not the aggregates, so any step other than Aggregate Price or Rounding
Values ordered after DDS is still rejected [Core]. The repo owner saw the same error
after dragging the aggregates up [Live, repo owner]. In a procedure with no DDS there
is no such boundary, and a formula after the aggregates saves (but see the lag in Rule 1).

What the tracked `RLM_DefaultPricingProcedure` ships today [Repo]:
- Every shipped `FormulaBasedPricing` step is **line-scope**: each has a `parentStep`
  and runs before DDS.
- Every `GroupingAndAggregatePricing` step is `SUM` over one line field. That's what
  ships, **not** a platform limit; the element also accepts `AVG`, `MAX` and `MIN`,
  but not `COUNT` [Core] (see
  [`elements/aggregate-price.md`](elements/aggregate-price.md)).
- There are **no** `RoundingValues` steps (checked in shipped expression-set XML), even though the DDS error names Rounding
  Rules.

## Rule 3: Aggregate Price after Derived Price, filtered to contributing lines

Help recommends placing the Aggregate Price element **after** the Derived Price element
and adding a **Where** condition that targets only the contributing lines [Help]. The
shipped aggregates do this with `DerivedPricingAttribute isNotNull` +
`DerivedPricingAttribute isFalse` conditions [Repo].

## Rule 4: don't build a pricing loop

A value that feeds itself never settles. Help's example: Net Unit Price is set from
Input Unit Price, and then an aggregate element that reads Net Unit Price changes Input
Unit Price. The result is a loop that causes slow or wrong pricing [Help]. Before
writing to a tag, trace what produces and what reads it:

```bash
python scripts/expression_sets/trace_expression_set.py --target-org <sf_alias> \
    --developer-name <name> --variable <Tag>
```

## Rule 5: every reprice reloads written values from the record

Before the procedure runs, each reprice loads a written field's **prior value from the
record** [Live, repo owner]. Two consequences:

- An element that writes a field only inside filtered branches never clears it. Reset
  the field on every line first, then let the branches overwrite it. See
  [`elements/assignment.md`](elements/assignment.md) and
  `../expression-sets/authoring-and-overlays.md` → *Conditional assignments*.
- Any element that reads a field before the element that recalculates it gets the
  previous reprice's value (Rule 1).

## Caveat: line margin is calculated before DDS, the header total after it

In `RLM_DefaultPricingProcedure`, per-line **cost and margin** (`ItemTotalCost__std`,
`ItemMarginAmount__std`) are calculated **before** DDS (in the
`Calculatecostandmarginforpricedlines` List Group), while `TotalAmount` is a
**post-DDS** aggregate [Repo]. No shipped aggregate sums cost or margin; if you add one
(an overlay), mind the base:

- `SUM(ItemTotalCost__std)`: header total cost isn't affected by DDS, so it's always
  correct.
- `SUM(ItemMarginAmount__std)`: header margin **amount** sums line margins from
  *before* the header discount. On a quote with a header discount, that margin is on a
  different base than `TotalAmount`, so a margin **percent** built from the two is
  internally inconsistent. With no header discount the bases match.

If you need a header margin percent, prefer a record-level formula field over a step
in the procedure (Rule 1), and state which base it uses.

## Removing a step leaves its context mapping inert

If you remove a step that *produced* a value a Context Definition mapping persists,
the mapping doesn't error. Nothing feeds it any more, so the field persists as
**null** on every reprice. When you drop a producing step, remove its context mapping
too, or knowingly accept it as inert [Live, repo owner]. Why a removal still validates
and reactivates: [`../expression-sets/authoring-and-overlays.md`](../expression-sets/authoring-and-overlays.md)
→ *Removing steps — validation is structural, not functional*.

## Activation after a decision table change

Don't activate a pricing procedure immediately after you change its decision tables.
Make a small change to the procedure, save it again, and then activate it, so it
doesn't deploy with outdated metadata [Help]. For refresh mechanics see
`../decision-tables/SKILL.md`.
