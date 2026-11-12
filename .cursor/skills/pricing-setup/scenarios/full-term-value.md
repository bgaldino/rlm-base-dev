# Scenario: A Full-Term Value Next to the Platform's One-Period Total

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`, indexed in [README.md](README.md).
> Release 264. No Help example; this is custom wiring on a clone of the pricing procedure.
> Sources are tagged `[Repo: <path>]`, `[inferred]` and `[Measured]` (measured 2026-11-11 on a
> fresh 264 `ent-sb0` scratch org). The example uses neutral round numbers.

**Goal:** a quote shows a full-term value, a full-term cost and a full-term margin (a
"commitment" or "contract value") next to the platform's quote total, plus an optional
deduction from revenue (a fee, say) on part of the value.

**Why the platform total isn't it.** The platform prices a Term Defined line for its whole
term, a One-Time line once, and an Evergreen line without an end date for one period: the
shipped procedure assigns it a term count of 1 through `EvergreenPricingTermCountConstant`
(see [../proration-and-selling-models.md → Default term counts](../proration-and-selling-models.md#default-term-counts)).
So a monthly support line counts one month in the quote total `[Measured]`. Don't raise the
Evergreen term count to get a full-term figure: it changes every Evergreen line's price.
Compute the full-term value in fields of its own.

## Prerequisite

Term-line cost must cover the whole term. Overlay the shipped cost formula with the guarded
× `PricingTermCount` version first:
[cost-and-margin.md → Term lines cost one period](cost-and-margin.md#term-lines-cost-one-period).

## Wiring, in order

| # | Layer | What | Where it's documented |
|---|---|---|---|
| 1 | Line fields | On `QuoteLineItem`: Currency fields *Full-Term Value*, *Full-Term Cost* and, for a value over a product subset, *Subset Value*. Grant field access in a permission set | `../../apex-security-hardening/SKILL.md` |
| 2 | Quote fields | On `Quote`: a Number field *Horizon Months* (the comparison horizon), a flag for the deduction (a checkbox or a picklist value), roll-up summaries (SUM) of the three line fields, and formula fields for the fee, net revenue and margin (step 5) | |
| 3 | Context | Map the line fields as `SalesTransactionItem` attributes and *Horizon Months* as a `SalesTransaction` attribute in the sales transaction context, with tags, so the procedure can read and write them. A line-level formula can read the header tag directly `[Measured]` | `../../context-service/SKILL.md` |
| 4 | Procedure | Four List Groups in a clone of the procedure, placed after `Calculatecostandmarginforpricedlines`, before the header-discount groups and Discount Distribution (a step after DDS is rejected; `../../pricing-procedures/procedure-anatomy-and-ordering.md`), and in this order (below). So *Full-Term Value* doesn't include a header discount that DDS distributes later `[inferred]` | `../../pricing-procedures/elements/list-group-and-list-operation.md`, `../../pricing-procedures/elements/formula-based-pricing.md` |
| 5 | Quote formulas | Fee, net revenue and full-term margin from the roll-ups (below) | |
| 6 | Reprice | Changing *Horizon Months* on the quote doesn't reprice the lines; run Reprice All (or change a line). A header-only save leaves line prices unchanged `[Measured]`. The fee flag needs no reprice, since only quote formulas read it | `../../transaction-line-editor/SKILL.md` |

### Procedure groups (row 4)

Each group is a List Group with an Advanced List Filter and one Formula-Based Pricing step.
A later group overwrites the fields an earlier one wrote for the lines it admits, so the
order matters `[Measured]`.

| # | Filter (all criteria ANDed) | Writes |
|---|---|---|
| a | `NetUnitPrice` IsNotNull | *Full-Term Value* = `ItemNetTotalPrice`; *Full-Term Cost* = `IF(ISNULL(ItemTotalCost__std), 0, ItemTotalCost__std)`; *Subset Value* = `0` |
| b | `SellingModelType` Equals `'Evergreen'`; `NetUnitPrice` IsNotNull; `ItemRampIdentifier` IsNull | *Full-Term Value* = `IF(ISNULL(<horizon>), ItemNetTotalPrice, ROUND(NetUnitPrice * LineItemQuantity * <horizon>, 2))`; *Full-Term Cost* = `IF(ISNULL(ItemUnitCost__std), 0, IF(ISNULL(<horizon>), IF(ISNULL(ItemTotalCost__std), 0, ItemTotalCost__std), ROUND(ItemUnitCost__std * LineItemQuantity * <horizon>, 2)))` |
| c | `SellingModelType` Equals `'Evergreen'`; `NetUnitPrice` IsNotNull; `ItemRampIdentifier` IsNotNull | *Full-Term Value* = `ROUND(NetUnitPrice * LineItemQuantity * 12, 2)`; *Full-Term Cost* = `IF(ISNULL(ItemUnitCost__std), 0, ROUND(ItemUnitCost__std * LineItemQuantity * 12, 2))` |
| d | A criterion that selects the subset; `NetUnitPrice` IsNotNull | *Subset Value* = `ItemNetTotalPrice` |

- **a** takes the platform totals: a term line's net total and its (term-corrected) cost
  already cover the whole term, and a One-Time line counts once.
- **b** counts a monthly Evergreen line for the horizon. `<horizon>` is the *Horizon Months*
  tag. The formula assumes a monthly pricing term; for another term, convert the horizon
  into that term's periods. With no horizon, both fields keep the platform's value and its
  matching term-corrected cost, so they cover the same periods.
- **c** handles a yearly group ramp: an Evergreen line repeats in every segment, so each
  segment's line counts 12 months and the segments together cover the horizon. For segments
  of another length, use their months. The filter needs ramp-stamped lines: the measured
  UI-built ramp stamped them, but an Evergreen bundle child added by API into
  already-ramped segments carries no ramp identifier
  (`../../ramped-quotes/bundle-children-lifecycle.md`) and would fall into group b, once per
  segment. A line field that counts each line's months from its quote line group's end date
  replaces group c and needs no ramp identifier; see
  [Amendments and ramps](#amendments-and-ramps-the-months-each-evergreen-line-counts).
- **d**: the sales transaction context has no product Family, and a roll-up summary filter
  can't use a field on another object, so you can't roll up "lines of family X" on the quote
  `[Measured]`. Write the subset value per line in the procedure and roll it up unfiltered.
  Filter on what the line context carries, such as `SellingModelType` Equals
  `'TermDefined'` for subscription lines `[Measured]`. If nothing it carries separates the
  subset, map a product field into the context first (`context-service`) `[inferred]`.
  Group d writes the platform net total, so keep Evergreen lines out of the subset: their
  base would be one period, not the horizon `[inferred]`.

### Quote formulas (row 5)

| Field | Type | Formula |
|---|---|---|
| Fee | Currency | `IF(<flag is set>, ROUND(<rate> * Subset_Value__c, 2), 0)` |
| Net Revenue | Currency | `Full_Term_Value__c - Fee__c` |
| Full-Term Margin | Number, 6 decimals | `IF(Net_Revenue__c = 0, NULL, (Net_Revenue__c - Full_Term_Cost__c) / Net_Revenue__c)` |

Here `Full_Term_Value__c`, `Full_Term_Cost__c` and `Subset_Value__c` are the quote roll-ups.
This margin is a ratio (0.57), while the line `Margin` field reads in percent units (57)
(see [cost-and-margin.md → Margin units](cost-and-margin.md#margin-units)). Keep the two apart
in reports.

## Amendments and ramps: the months each Evergreen line counts

Group b counts every Evergreen line for the whole horizon. On a mid-term amendment that
overstates the value: an Evergreen delta line was multiplied by the whole horizon `[Measured]`.
Count, per line, the months it covers, in a line field the procedure reads.

**Where an amendment's commitment start is.** An amendment quote has no `ContractId` or
`RelatedQuoteId`; its lines have no asset lookup (`BillingReference` is text); the sales
transaction context hydrates no Asset node for a quote; an Evergreen asset has no
`LifecycleEndDate`; and a quote roll-up of MAX(line `EndDate`) is blank when the amendment
has no Term line `[Measured]`. What every amended line has is `QuoteLineItem.QuoteActionId`
→ `QuoteAction` (`Type` Amend) → `SourceAsset.LifecycleStartDate` `[Measured]`. Nor can a
line formula read its parent line: a formula that spans `ParentQuoteLineItem` fails to
deploy ("Field ParentQuoteLineItem does not exist") `[Measured]`.

Field names below are examples; use your own.

| # | Layer | What |
|---|---|---|
| 1 | Quote field | Date `Commitment_Start__c` |
| 2 | Flow | Record-triggered on `QuoteLineItem`, after save, on **create and update**: when `QuoteAction.Type` is Amend and `QuoteAction.SourceAsset.LifecycleStartDate` is set, stamp the quote's `Commitment_Start__c` with the earliest such start, as the GMT date: `DATEVALUE(LEFT(TEXT(<datetime>), 10))`. `QuoteAction` isn't triggerable, and the amend API sets `QuoteActionId` after it inserts the line, so a create-only trigger misses it. Plain `DATEVALUE` on the midnight-GMT start returned the previous day in a US user's time zone `[Measured]` |
| 3 | Line formula | Number `Months_Counted__c` (below) |
| 4 | Context | Map `Months_Counted__c` as a `SalesTransactionItem` attribute, INPUT, with a tag. A formula field mapped INPUT hydrates into pricing `[Measured]` |
| 5 | Procedure | Group b multiplies by `<months>` (that tag) where it's set, else by `<horizon>` (formulas below), and drops its `ItemRampIdentifier` criterion; group c is removed, since the field counts a segment's months |

```text
IF(ISBLANK(StartDate), NULL,
  IF(NOT(ISBLANK(QuoteLineGroup.EndDate)),
    (YEAR(QuoteLineGroup.EndDate) * 12 + MONTH(QuoteLineGroup.EndDate))
      - (YEAR(StartDate) * 12 + MONTH(StartDate)) + 1,
    IF(OR(ISBLANK(Quote.Horizon_Months__c),
          ISBLANK(BLANKVALUE(Quote.Commitment_Start__c, Quote.StartDate))), NULL,
      MAX(0, Quote.Horizon_Months__c
        - ((YEAR(StartDate) * 12 + MONTH(StartDate))
          - (YEAR(BLANKVALUE(Quote.Commitment_Start__c, Quote.StartDate)) * 12
             + MONTH(BLANKVALUE(Quote.Commitment_Start__c, Quote.StartDate))))))))
```

That is: in a dated quote line group (a ramp segment), the months from the line's start to
the group's end; otherwise *Horizon Months* less the calendar months from the commitment start
(the stamp, else the quote's `StartDate`) to the line's start, never below 0. It assumes
segments and the commitment start on the 1st of a month: the formula counts calendar months
and ignores the day, so a segment from 2027-02-15 to 2028-02-14 counts 13. Every measured date
was the 1st of a month. The pricing engine prorates by days (the first and last partial period
count days used over the days in that period, `[Platform behaviour, traced]`; see
[proration](../proration-and-selling-models.md)), so off the 1st this months value and the line's
`PricingTermCount` diverge; decide which one the source's number follows and do not expect the two to match
(doc-only; not measured live). *Horizon
Months* on the amendment quote must hold the original commitment's length (a field default
does it when every commitment has the same length) `[inferred]`.

Group b's formulas become:

- *Full-Term Value* = `IF(ISNULL(<months>), IF(ISNULL(<horizon>), ItemNetTotalPrice, ROUND(NetUnitPrice * LineItemQuantity * <horizon>, 2)), ROUND(NetUnitPrice * LineItemQuantity * <months>, 2))`
- *Full-Term Cost* = `IF(ISNULL(ItemUnitCost__std), 0, IF(ISNULL(<months>), IF(ISNULL(<horizon>), IF(ISNULL(ItemTotalCost__std), 0, ItemTotalCost__std), ROUND(ItemUnitCost__std * LineItemQuantity * <horizon>, 2)), ROUND(ItemUnitCost__std * LineItemQuantity * <months>, 2)))`

`<months>` is blank where nothing maps the field (an order, say), and those lines keep the
horizon.

- **Reprice after creating the amendment.** The stamp lands after the amendment's lines are
  created, so the first price of a new amendment still counts the whole horizon. A full
  reprice afterwards reads it (measured: every line PATCHed through Place with pricing
  `Force`) `[Measured]`.
- **Measured shape.** A mid-term add on an Evergreen asset counted only the months left; a
  support-only amendment that reduced one Evergreen asset and added a new Evergreen line
  counted the months left on both, the new line (which has no source asset) through the
  quote's stamp; every case matched its expected full-term value, and new-sale values
  didn't change `[Measured]`.
- **A price change dated on a renewal start.** The stamp reads the source asset's lifecycle start, which
  `[Platform behaviour, traced]` is the only route from an amendment line to a contract start (the line's own start is
  the amendment date). On a change dated on a renewal's start, the formula then counts the months from the
  original start, which can leave 0 months to the horizon. A custom months-remaining value counted from the original commitment start was 0 for a price change dated at the renewal start `[Measured: 2026-11-12, 264, scratch; one org]`; the line's own change value and billing schedules were unaffected. What a renewed asset's lifecycle
  start is was not traced. Fix `[inferred]`: if the asset's lifecycle start is the original start, stamp the start of the current term instead.
- **Not stamped:** a new-sale quote and a renewal quote. The formula counts from their own
  `StartDate`.
- **Ramps.** An Evergreen line in a dated quote line group counts that segment's months, so
  segments that span the horizon count it between them `[Measured]`. This also covers an
  Evergreen line added to every segment unramped: it carries no ramp identifier and gets no
  ramp uplift `[Measured]`, so group c's filter would miss it and group b would count it for
  the whole horizon once per segment.

## Example (neutral numbers)

Horizon 24 months; fee 5% of subscription value when the flag is set.

| Line | Selling model | Price | Cost | Platform total | Full-term value | Full-term cost | Subset |
|---|---|---|---|---|---|---|---|
| Subscription | Term Defined, 2 `Annual` | 1,000 / year | 400 / year | 2,000 | 2,000 | 800 | 2,000 |
| Support | Evergreen, monthly | 100 / month | 40 / month | 100 | 2,400 | 960 | 0 |
| Setup | One-Time | 500 | 300 | 500 | 500 | 300 | 0 |
| **Quote** | | | | **2,600** | **4,900** | **2,060** | **2,000** |

Flag set: fee 100, net revenue 4,800, margin (4,800 − 2,060) / 4,800 = 0.570833.
Flag not set: fee 0, net revenue 4,900, margin 0.579592.

In a yearly group ramp of two segments the support line appears once per segment; each
counts 1,200 and the total is again 2,400. One-Time children of a configurable bundle also
repeat in every segment of a UI-built group ramp, and both the platform total and the
full-term value count each repeat `[Measured]`; see
`../../ramped-quotes/bundle-children-lifecycle.md` before you ramp such a bundle.

## Verify

```bash
sf data query -q "SELECT Product2.Name, ProductSellingModel.SellingModelType, TotalPrice, TotalCost, Full_Term_Value__c, Full_Term_Cost__c, Subset_Value__c FROM QuoteLineItem WHERE QuoteId = '<quote>'" --target-org <sf_alias>
sf data query -q "SELECT TotalPrice, Full_Term_Value__c, Full_Term_Cost__c, Subset_Value__c, Fee__c, Net_Revenue__c, Full_Term_Margin__c FROM Quote WHERE Id = '<quote>'" --target-org <sf_alias>
```

Use your own field API names. Check each line against the table above (term and One-Time
lines equal their platform totals; Evergreen lines equal per-period net × horizon, or × the
line's months counted on an amendment or in a group ramp), then
the quote roll-ups and formulas by hand. On an amendment, read the quote's
`Commitment_Start__c` and each line's `Months_Counted__c` after the reprice.

## Open questions

- Header discounts: whether *Full-Term Value* should carry a header discount, and how, is
  untested.
- Carrying the values to the order (the same fields on `OrderItem` and `Order`, mapped for
  the order) was not part of this measurement.
