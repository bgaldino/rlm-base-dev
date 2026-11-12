# Building a Compound group ramp in the quote UI (264)

> Sub-file of `.cursor/skills/ramped-quotes/SKILL.md`.

A rep can build a group ramp in the 264 quote editor with the same result as the API build:
- one shared `RampIdentifier`;
- a `SegmentIdentifier` per line;
- the uplift type on every ramp-stamped line;
- uplifting prices.

**Compound** was verified through order and activation, which created one Asset with an
`AssetStatePeriod` per segment. **Standard** was verified through pricing only.

**Measured** 2026-10-29 on a fresh `ent-r1` build of `main`:
- Org: 264.9.6, Advanced Detail Line Pricing on, Multiple Ramp Schedules Per Transaction on,
  procedure plan inactive.
- Product `QB-API`, list price 15,000. An attribute-based price adjustment (waterfall row
  *Calculate attribute-based prices*) takes 5,000 off, so the base is 10,000.

**Re-measured 2026-11-11** on fresh 264 `ent-sb0` scratch orgs (two orgs, Compound, a 0% first segment
and the same uplift in segments 2 and 3) with a configurable bundle whose children are Term Annual, Evergreen and One-Time, CML rules on.
These runs changed steps 1, 3 and 4 below and added
[What the segment uplift reaches](#what-the-segment-uplift-reaches).

## Steps

1. **Create the ramp schedule.** Create the quote. In the line editor, click **Create Ramp
   Schedule** (header button) and set:
   - Segment Type **Annual**, a start date, Duration **36**, Trial Segment **No**;
   - each segment's **Unit Price Uplift %** (for example 0 / 10 / 10).

   Save. **Trial Segment defaults to Yes** (30 days at a 100% discount), which shifts every
   segment by a month, so change it to No unless you want a trial (measured 2026-11-11, fresh 264
   `ent-sb0` scratch org). The name field is prefilled ("3 Year Ramp Schedule" for 36 months).
2. **For Compound, set the uplift type.** On the schedule, open Show Actions → **Edit Ramp
   Schedule**. **Ramp Uplift Type** is a per-segment picklist: setting one segment to **Compound**
   sets all of them and the parent `RampScheduleGroup`. Save. For Standard (the default), skip
   this step.
3. **Add the product to the segments.** On the **Year 1** segment row, open Show Actions →
   **Browse Catalogs**. In the 2026-11-11 runs (fresh 264 `ent-sb0` scratch orgs) it asked for the
   **catalog first**, then **Select Segments to Add Products**; the 2026-10-29 run recorded the segment
   prompt first; the cause of the difference isn't established, so check which comes first before a
   demo. Either way, the segment prompt offers:
   - Choose **Current and Subsequent Segments**. The dialog says it "adds rampable products as
     ramped line items". One add places the product in every segment, with ramp identity.
   - **Current Segment Only** "adds products as non-ramped line items" (dialog text; not tested).
4. **Pick the product and save.**
   - `Product2.CanRamp` gates the line-ramp path. A `CanRamp = false` product uplifts in an
     **API-built** group ramp (re-measured 2026-10-28/29). Through this dialog (measured 2026-11-05/06 on a
     different 264 org) a `CanRamp = false` term product was ramp-stamped; a standalone one-time product landed in every
     segment unstamped.
   - Bundles with a one-time child, added through Browse Catalogs (measured 2026-11-05/06 on the same org): adds failed with `UNKNOWN_EXCEPTION` until `IsDefault`
     was set true on the `ProductSellingModelOption` rows of the bundle and its children (which row matters wasn't
     isolated). Unticking an optional child in segment 2 or 3's configurator removed it from that segment and later ones
     in the test (segment 1 not tested; no constraint model referenced the bundle); a required child can't be removed.
     A child that a CML rule sizes is silently re-added instead (2026-11-11); a root answer that zeroes it in
     segment 2 does remove it from segment 2 on: see
     [Limiting a one-time child to segment 1](bundle-children-lifecycle.md#limiting-a-one-time-child-to-segment-1). A configurable bundle added with
     *Current and Subsequent Segments* puts every child, One-Time and Evergreen too, in every segment, and a CML-sized
     default component can split into two instances: see
     [What a UI-built bundle ramp carries](bundle-children-lifecycle.md#what-a-ui-built-bundle-ramp-carries).
     Amend, assetization and removal results:
     [bundle-children-lifecycle.md](bundle-children-lifecycle.md). No Amend action was found on the asset pages, so amend
     and cancel were run through the API on UI-built quotes.
   - **A CML-sized bundle added straight into the segments doesn't come in at its answers' sizes** (2026-11-11,
     two fresh 264 `ent-sb0` scratch orgs, rules on). Added without configuring it first: on one org every
     component was at quantity 1 in every segment while the stored answer kept its value, and opening segment 1's
     configurator then showed that answer solved down to fit those lines (it read as 1); on the other org the
     bundle came in sized for a sizing answer of 1. Re-entering the answer and saving re-derived every quantity
     in every segment. So re-enter the answers in segment 1's configurator after the add
     (placing the bundle already sized through the API was not measured in a group ramp). Configuring it
     in the Browse Catalogs dialog before the add, on a ramp quote whose model held a cross-line check,
     showed the answer at 1 with that check's error and Save disabled (one run).
     Why the add lands at quantity 1 is consistent with this, not shown for this path: a placement with no
     configuration choice skips the rules, so lines arrive at default quantities, and the configurator then
     reconciled the stored answer to those lines [Platform behaviour, traced in part]. The UI add call
     itself wasn't traced and which side the solver gives way on is engine behaviour, so treat the
     answer-solved-down result as measured, not as a platform rule.
   - Use a **term** selling model (for example Term Annual) for a standalone product. On the API path an
     Evergreen price book entry can't ramp and the segments come out without ramp identity. Through this
     dialog too, a standalone Evergreen product added with *Current and Subsequent Segments* landed in every
     segment with no `RampIdentifier` and took no uplift (2026-11-11; see
     [What the segment uplift reaches](#what-the-segment-uplift-reaches)). An Evergreen **bundle child** added
     through it was ramp-stamped in every segment (2026-11-11).
   - **Reprice All** is a toolbar button. Prices were already uplifted before it was clicked.

## Expected result

| Segment | `UnitPriceUplift` | `ApplUnitPriceUpliftPct` Compound / Standard | `NetUnitPrice` Compound / Standard |
|---|---|---|---|
| Year 1 | 0 | 0 / 0 | 10,000 / 10,000 |
| Year 2 | 10 | 10 / 10 | 11,000 / 11,000 |
| Year 3 | 10 | 21 / 10 | 12,100 / 11,000 |

**Order and activation (Compound quote):**
- The order lines keep the `RampIdentifier`.
- Activation creates **one** Asset with three `AssetStatePeriod` rows: `Mrr` 833.33 / 916.67 /
  1,008.33.
- `Amount` was 0 on these rows; check `Mrr`.

**The price waterfall shows no ramp-uplift row.** On the Compound quote's Year 3 line it goes from
the 10,000 adjusted price straight to Net Unit Price 12,100. To see the uplift, read
`ApplUnitPriceUpliftPct`.

Year 1's 0 / 0 is from the 2026-10-29 run. On the 2026-11-11 UI builds, segment 1 (0%) read **null** for
both `UnitPriceUplift` and `ApplUnitPriceUpliftPct`; treat null as 0 when checking segment 1.

These round numbers hide the precision: the uplifted price is **not rounded** to cents. See
[`compound-uplift.md`](compound-uplift.md) → Precision.

## What the segment uplift reaches

Measured 2026-11-11 on two fresh 264 `ent-sb0` scratch orgs, Compound, a bundle with Term, Evergreen
and One-Time children:

- **The segment's Unit Price Uplift % is applied to every ramp-stamped line in that segment**: Term, Evergreen and
  One-Time lines alike (each carries the segment's `UnitPriceUplift` and the compounded
  `ApplUnitPriceUpliftPct`; segment 1, at 0%, read null for both fields, not 0). Their
  `NetUnitPrice` uplifts too.
- **A line without ramp identity takes none.** A standalone Evergreen product added with *Current and
  Subsequent Segments* had no `RampIdentifier` in any segment; in segments 2 and 3 it carried the
  segment's `UnitPriceUplift`, but its `ApplUnitPriceUpliftPct` was blank and its `NetUnitPrice` stayed at the segment 1 price (one org; the other confirmed the missing
  `RampIdentifier`). It needs no `UnitPriceUplift` 0 exemption.
- **On the Evergreen and One-Time lines `TotalPrice` didn't follow**: it stayed at quantity × the
  un-uplifted price in every segment (`NetTotalPrice` wasn't read), so line totals disagreed with
  quantity × net. Term lines' `TotalPrice` did follow.
- **`UnitPriceUplift` 0 on a line exempts it.** Setting it to 0 on the Evergreen and One-Time lines of
  segments 2 and 3 (Place PATCH), then **Reprice All**, brought them back to the un-uplifted price
  with consistent totals. Use it when only some products should escalate (a filter on the
  procedure's ramp uplift step is an alternative; not measured).
- That partial PATCH also re-uplifted the lines it didn't touch (one org). Source shows that untouched lines
  are re-run, and a non-idempotent uplift re-applied, when delta pricing is off or its conditions don't all
  hold; with it on, only the edited lines and their dependents re-run [Platform behaviour, traced]. The
  measured org was Foundations-built (delta pricing enabled by the org definitions) but its setting wasn't
  read there (live check). See SKILL.md → DO NOT (partial PATCH on a compound ramp). Always finish a ramp line edit with
  **Reprice All**.

## Verify

```bash
sf data query --target-org <sf_alias_or_username> -q "SELECT SegmentName, RampIdentifier, \
  SegmentIdentifier, RampUpliftType, UnitPriceUplift, ApplUnitPriceUpliftPct, NetUnitPrice, \
  QuoteLineGroup.Name FROM QuoteLineItem WHERE QuoteId = '<quote Id>' ORDER BY StartDate"
# After activation: one Asset per product, one AssetStatePeriod per segment
sf data query --target-org <sf_alias_or_username> -q "SELECT AssetId, StartDate, EndDate, Mrr \
  FROM AssetStatePeriod WHERE Asset.AccountId = '<account Id>' \
  AND Asset.Product2.StockKeepingUnit = '<SKU>' ORDER BY AssetId, StartDate"
```

**Pass** when all of these hold:
- one non-null `RampIdentifier`;
- a distinct `SegmentIdentifier` per line;
- the expected `RampUpliftType`;
- `NetUnitPrice` as in the table.

## Relation to the September measurement

In September, on `ramp264b`, a quote with lines inside group segments had no `RampIdentifier` and
flat prices. GitHub #185 reports one Asset per line after activation.

**The cause isn't established.** Placing a product into a segment through the UI was never done in
September, so there is no like-for-like comparison. A simple explanation would be that those lines
were added with **Current Segment Only**, or from an Evergreen price book entry.

If a quote shows that symptom:
1. Check which choice was used.
2. Check the line's selling model is a term model, not Evergreen.
3. Compare the org's ramp settings with a fresh build.

**Line ramps** (line row → Show Actions → **Ramp**):
- They had no uplift control in the September measurement.
- `RLM_DefaultPricingProcedure` applies no uplift to them (measured 2026-10-28).

Prefer group ramps.
