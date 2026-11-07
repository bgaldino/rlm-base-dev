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
  `interfaceSourceType: PricingProcedure` and `usageType: DefaultPricing` ("Pricing" in
  the UI), plus a **usage subtype** (Revenue Cloud, Commerce, Insurance, …) and a
  **context definition** (`SalesTransactionContext` or an extension of it) [Help].
  Element lookups offer only the decision tables from pricing recipes assigned to that
  subtype [Help]. You can change the subtype when you clone a procedure, not when you
  edit it [Help].
- **Each element is one step.** Elements read and write **context tags** (for example
  `ListPrice`, `NetUnitPrice`, `ItemNetTotalPrice`). Variables are mapped to tags, and
  the tags carry values from one element to the next [Help].
- **Scope comes from placement.** An element at the top level runs over the whole
  transaction. An element inside a **List Group** runs only on the lines that the
  group's **List Operation** (`AdvancedListFilter`) lets through. In metadata both are
  flat `<steps>` entries: a child names its group in `parentStep`, and `sequenceNumber`
  restarts at 1 under each parent [Repo]. See
  [`elements/list-group-and-list-operation.md`](elements/list-group-and-list-operation.md).
- **Branching uses mutually exclusive lanes.** Contract pricing, derived pricing,
  last-transaction pricing and the plain path are separate List Groups whose filters
  exclude each other (for example "without derived or last-transaction pricing"). A
  line that matches two lanes is priced twice [Repo, inferred].
- **Versions and rank.** If more than one enabled version matches, the engine uses the
  version whose rank is **greatest** [Help, discovery only]. For pricing
  procedures it is unconfirmed (see [operations-and-troubleshooting.md](./operations-and-troubleshooting.md)
  section 2).
- **Include in Output.** At least one element must have *Include in Output* selected,
  or the procedure returns nothing for downstream processing [Help].
- **Local list variables** hold a value that one element calculates so a later element
  can reuse it, without a context tag. The element that writes the variable must come
  **before** the element that reads it, or the read resolves to null. They can't be
  passed in from outside, and Map Line Item and Price Propagation can't use them [Help].

## The phase order the shipped default follows (snapshot)

`RLM_DefaultPricingProcedure` has 42 top-level steps. Grouped into phases, they run in
this order. This is a snapshot that will age; print the live tree with
`python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name>`.

| # | Phase | Elements (actionType) | Why here |
|---|---|---|---|
| 1 | Set up | Pricing Setting (`PricingSettings`) | Maps the standard pricing variables. Always first |
| 2 | Detail lines | Map Line Item (`BreakdownLineMapping`) | Maps item → item detail. Put it right after Pricing Setting |
| 3 | Inputs | Assignment, contract defaulting lanes | Sets pricing contract and pricing date before any lookup reads them |
| 4 | Base price | List Price (`ListPrice`) from the price book and the cost book | Fills `ListPrice` and unit cost |
| 5 | Choose a lane | List Groups: contract, derived, last-transaction, plain | Sets `InputUnitPrice` → `NetUnitPrice` once per line |
| 6 | Adjustments | Attribute (`AttributeDiscount`), Bundle (`BundleDiscount`), Volume (`VolumeDiscount`), Manual (`ManualDiscount`) | Each one discounts the running `NetUnitPrice` |
| 7 | Revisions | Price Revision (`PriceRevision`): non-ramp and ramp/compound | Uplift or CPI on top of the discounted price |
| 8 | Term pricing | Proration (`Proration`) + Subscription Price (`SubscriptionPricing`) | Turns the unit price into a term amount |
| 9 | Line totals | Formula-Based Pricing (`FormulaBasedPricing`) for cost/margin, Assignment for subtotals | Line-level formulas run **before** the closing block |
| 10 | Header inputs | List Groups that apply header discount or price override | Sets header values for DDS to distribute |
| 11 | Distribute | Discount Distribution Service (`DiscountDistributionService`) | Rewrites line `NetUnitPrice` / `ItemNetTotalPrice` |
| 12 | Roll up | Aggregate Price (`GroupingAndAggregatePricing`) ×3 | `TotalAmount`, `Subtotal`, `ItemGroupSummarySubtotal` |

Phases 11–12 (plus Rounding Values when present) make up the **closing block**, the
fixed final section of the procedure. The rules below are about that block.

## Rule 1: no `FormulaBasedPricing` after the closing block

The closing block is Discount Distribution Service (`DiscountDistributionService`), the
`GroupingAndAggregatePricing` aggregate steps, and Rounding Rules. A
`FormulaBasedPricing` step placed **after** it is rejected, and the error message is
**misleading**: it names DDS, not your formula step [Live, repo owner]:

```
INVALID_INPUT: You can add the Discount Distribution Service element only
before the Rounding Rules and Aggregate elements …
```

The real cause is ordering. A header-scope formula that depends on aggregate outputs
can't sit after the closing block. This has two consequences for an overlay that adds
a formula computed *from* aggregate results:

- Place new `GroupingAndAggregatePricing` steps with `afterStep` anchored to the
  **last existing aggregate**. They slot into the aggregate band cleanly.
- A `FormulaBasedPricing` step that uses those aggregate outputs has **no position
  that is both accepted and fed fresh values**. You *can* add a header-scope formula: a
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
wrong total. The Rule 1 restriction also moves with the aggregate elements; it isn't
tied to a fixed position. Dragging the aggregates up just drags the "no formula after
aggregates" boundary up with them [Live, repo owner].

What the tracked `RLM_DefaultPricingProcedure` ships today [Repo]:
- Every shipped `FormulaBasedPricing` step is **line-scope**: each has a `parentStep`
  and runs before DDS.
- Every `GroupingAndAggregatePricing` step is `SUM` over one line field. That's what
  ships, **not** a platform limit; the element also accepts `AVG`, `MAX` and `MIN`,
  but not `COUNT` [Core] (see
  [`elements/aggregate-price.md`](elements/aggregate-price.md)).
- There are **no** `RoundingValues` steps, even though the DDS error names Rounding
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
**post-DDS** aggregate [Repo]:

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
