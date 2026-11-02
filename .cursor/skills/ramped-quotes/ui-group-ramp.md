# Building a Compound group ramp in the quote UI (264)

> Sub-file of `.cursor/skills/ramped-quotes/SKILL.md`.

A rep can build a group ramp in the 264 quote editor with the same result as the API build:
- one shared `RampIdentifier`;
- a `SegmentIdentifier` per line;
- the uplift type on every line;
- uplifting prices.

**Compound** was verified through order and activation, which created one Asset with an
`AssetStatePeriod` per segment. **Standard** was verified through pricing only.

**Measured** 2026-10-29 on a fresh `ent-r1` build of `main` (todo 178, GitHub #185):
- Org: 264.9.6, Advanced Detail Line Pricing on, Multiple Ramp Schedules Per Transaction on,
  procedure plan inactive.
- Product `QB-API`, list price 15,000. An attribute-based price adjustment (waterfall row
  *Calculate attribute-based prices*) takes 5,000 off, so the base is 10,000.

## Steps

1. **Create the ramp schedule.** Create the quote. In the line editor, click **Create Ramp
   Schedule** (header button) and set:
   - Segment Type **Annual**, a start date, Duration **36**, Trial Segment **No**;
   - each segment's **Unit Price Uplift %** (for example 0 / 10 / 10).

   Save.
2. **For Compound, set the uplift type.** On the schedule, open Show Actions → **Edit Ramp
   Schedule**. **Ramp Uplift Type** is a per-segment picklist: setting one segment to **Compound**
   sets all of them and the parent `RampScheduleGroup`. Save. For Standard (the default), skip
   this step.
3. **Add the product to the segments.** On the **Year 1** segment row, open Show Actions →
   **Browse Catalogs**. The first prompt is **Select Segments to Add Products**:
   - Choose **Current and Subsequent Segments**. The dialog says it "adds rampable products as
     ramped line items". One add places the product in every segment, with ramp identity.
   - **Current Segment Only** "adds products as non-ramped line items" (dialog text; not tested).
4. **Pick the product and save.**
   - `Product2.CanRamp` gates the line-ramp path. A `CanRamp = false` product uplifts in an
     **API-built** group ramp (pack 174, re-measured 2026-10-28/29). The UI test used `QB-API`
     (`CanRamp = true`); a `CanRamp = false` product in this dialog wasn't tried.
   - Use a **term** selling model (for example Term Annual). On the API path an Evergreen price
     book entry can't ramp and the segments come out without ramp identity (pack 174); not tried
     in this dialog.
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
