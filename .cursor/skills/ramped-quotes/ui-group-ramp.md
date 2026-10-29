# Building a Compound group ramp in the quote UI (264)

A rep can build a Standard or Compound group ramp end to end in the 264 quote editor. The result
matches the API build: one shared `RampIdentifier`, a `SegmentIdentifier` per line, the uplift type
on every line, compounding prices, and one Asset with an `AssetStatePeriod` per segment.

Measured 2026-10-29 on a fresh `ent-r1` build of `main` (264.9.6, Advanced Detail Line Pricing on,
Multiple Ramp Schedules Per Transaction on, procedure plan inactive), product `QB-API`
(list 15,000; ADLP takes 5,000 off, so the base is 10,000). Todo 178, GitHub #185.

## Steps

1. Create the quote, then in the line editor click **Create Ramp Schedule** (header button).
   Segment Type **Annual**, a start date, Duration **36**, Trial Segment **No**. In each segment's
   **Unit Price Uplift %** cell type the uplift (for example 0 / 10 / 10). Save.
2. For Compound: on the schedule, Show Actions → **Edit Ramp Schedule**. **Ramp Uplift Type** is a
   per-segment picklist; setting one segment to **Compound** sets all of them and the parent
   `RampScheduleGroup`. Save. Skip this step for Standard (the default).
3. On the **Year 1** segment row, Show Actions → **Browse Catalogs**. The first prompt is
   **Select Segments to Add Products**:
   - **Current and Subsequent Segments** ("adds rampable products as ramped line items"): one add
     places the product in every segment with ramp identity. Use this.
   - **Current Segment Only** ("adds products as non-ramped line items"), per the dialog text; not
     tested.
4. Pick the product and save. `Product2.CanRamp` gates only the line-ramp path, not this one.
   **Reprice All** is a toolbar button. Prices were already uplifted before it.

## Expected result

| Segment | `UnitPriceUplift` | `ApplUnitPriceUpliftPct` Compound / Standard | `NetUnitPrice` Compound / Standard |
|---|---|---|---|
| Year 1 | 0 | 0 / 0 | 10,000 / 10,000 |
| Year 2 | 10 | 10 / 10 | 11,000 / 11,000 |
| Year 3 | 10 | 21 / 10 | 12,100 / 11,000 |

Order and activation (Compound quote): the order lines keep the `RampIdentifier`, and activation
creates **one** Asset with three `AssetStatePeriod` rows (`Mrr` 833.33 / 916.67 / 1,008.33).

The price waterfall has **no row for the ramp uplift**: it goes from the ADLP-adjusted price
straight to Net Unit Price. Read `ApplUnitPriceUpliftPct` to see the uplift, not the waterfall.

## Verify

```bash
sf data query -o <sf_alias_or_username> -q "SELECT SegmentName, RampIdentifier, SegmentIdentifier, \
  RampUpliftType, UnitPriceUplift, ApplUnitPriceUpliftPct, NetUnitPrice, QuoteLineGroup.Name \
  FROM QuoteLineItem WHERE QuoteId = '<quote Id>' ORDER BY StartDate"
```

Pass: one non-null `RampIdentifier`, distinct `SegmentIdentifier`s, the expected `RampUpliftType`,
and `NetUnitPrice` as in the table. After activation, one Asset per product with one
`AssetStatePeriod` per segment.

## What changed since the September measurement

In September, on an older org (`ramp264b`), a quote with lines inside group segments had no
`RampIdentifier` and flat prices, and GitHub #185 reports one Asset per line after activation. Placing
a product into a segment in the UI was never done then (a harness limit). On the fresh 264 build
the **Current and Subsequent Segments** choice stamps identity and everything works. An upgraded
org is not evidence about fresh builds; if an upgraded org still shows the September behavior,
compare its ramp settings with a fresh build first.

Line ramps (line row → Show Actions → **Ramp**) still have no uplift control, and
`RLM_DefaultPricingProcedure` applies no uplift to them. Prefer group ramps.
