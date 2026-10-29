# Price revision and CPI (Price Index) policies (264)

> Sub-file of `.cursor/skills/pricing-wiring/SKILL.md`.

How a **Price Revision Policy** changes a price in `RLM_DefaultPricingProcedure`, how CPI data is
seeded, and how to check a result. Measured 2026-10-29 on a fresh 264 build with the quote
procedure plan inactive (todo 314).

## What's involved

| Piece | Where |
|---|---|
| `IndexRate` (Region, Rate, `UsageType` Pricing, valid dates) | seeded by `datasets/sfdmu/qb/en-US/qb-price-revision/` |
| `Index_Rate_Decision_Table` (source `IndexRate`) | refreshed by `refresh_all_decision_tables` (`refresh_dt_default_pricing`) |
| `PriceRevisionPolicy` (`Flat` or `PriceIndex`, Formula, Region, effective dates) | the same plan |
| Renewal step `AdjustNetUnitPriceandSubtotalbyusingpricerevision` | `RLM_DefaultPricingProcedure` |
| Ramp step `Uplift` (a PriceRevision element) | `RLM_DefaultPricingProcedure` |

**The renewal step runs** only when all of these hold:
- `ItemPricingSource = LastTransaction`;
- the line isn't a derived-price line;
- the action is `Renew`;
- the line has a policy formula;
- the line isn't in a ramp (`ItemRampIdentifier` is null).

A blank lifecycle asset defaults to `LastTransaction` (PR #647).

**Formula terms:** `PolicyAdjustment` is the line's `UnitPriceUplift`. `PriceIndex` is the
decision-table rate for the policy's Region on the line's date. The step's `Rate` output is bound to
`ItemConsumerPriceIndex__std`, as in the 264 template (PR #646).

## Use it

1. Build with `qb=true`, or load the plan and refresh the table:
   ```bash
   cci task run insert_qb_price_revision_data --org <alias>
   cci task run refresh_dt_default_pricing --org <alias>
   ```
2. **Renewal:**
   1. Renew an asset as-is (`initiateRenewal`, Quote output).
   2. On the renewal line, set `PriceRevisionPolicyId` and, optionally, `UnitPriceUplift`. Both
      fields are on the RLM quote line layout.
   3. Reprice.
3. **Ramp:** set the policy on each group-ramp segment line, then reprice.

## Expected results

| Case | Result |
|---|---|
| As-is renewal from 2027-05-01 of a 2,400 asset, `QB US CPI Plus Adjustment`, uplift 2 | **2,520** = 2,400 × (1 + 3% + 2%), the 2027 rate |
| Same renewal, `QB Flat Uplift`, uplift 2 | **2,448** |
| Compound group ramp, list 3,240, segment uplift 0 / 10 / 10, CPI policy | 3,337.20 / 3,654.72 / 3,648.24 (applied 3 / 12.8 / 12.6) |
| Same ramp, Flat policy | 3,240 / 3,564 / 3,920.40 (applied 0 / 10 / 21) |

**Under CPI a ramp segment doesn't compound.** Each segment gets its own year's rate plus its uplift.
Core allows compounding only with a Flat policy or no policy.

On an as-is renewal the price sits on the detail line (`QuoteLineDetail`), and the parent
`NetUnitPrice` is null. Read the detail lines (see `rlm-business-apis/SKILL.md` → *Where an ARC
line's price lives*).

## Verify

```bash
sf data query --target-org <sf_alias_or_username> -q "SELECT QuoteLineItem.StartDate, Quantity, \
  NetUnitPrice FROM QuoteLineDetail WHERE QuoteLineItem.QuoteId = '<QUOTE_ID>'"
sf data query --target-org <sf_alias_or_username> -q "SELECT StartDate, NetUnitPrice, \
  ApplUnitPriceUpliftPct, PriceRevisionPolicyId FROM QuoteLineItem WHERE QuoteId = '<QUOTE_ID>' \
  ORDER BY StartDate"
```

Open the line's price waterfall. The Price Revision row should show `PolicyType`, `Rate` (the index
rate) and `PolicyAdjustment`, and it should **appear once**.

## Gotchas

- **The procedure plan doubles a renewal price revision.** With `RLM_Quote_Pricing_Procedure_Plan`
  active, the Revenue Settings default procedure runs again after the plan, and the revision
  compounds: 2,400 → 2,544 → 2,696.64 for 4% + 2. The plan is built inactive by default
  (`procedureplans_active: false`); see `datasets/sfdmu/procedure-plans/README.md` → *Activation*.
- **Region** on `IndexRate` and `PriceRevisionPolicy` is an unrestricted picklist with no values.
  The API takes any value, so no Setup step is needed.
- **Index rate ranges for one Region can't overlap.** Two policies can't share the same effective
  dates either ("The selected effective dates are already in use"). A hand-made policy for the same
  years makes the plan's rows fail; remove or re-date it first.
- **Stale table.** After adding or changing an `IndexRate`, refresh `Index_Rate_Decision_Table`.
  Until then, CPI prices with the old rates, or with no rate at all.
