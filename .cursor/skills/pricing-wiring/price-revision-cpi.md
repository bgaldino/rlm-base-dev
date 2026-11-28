# Price revision and CPI (Price Index) policies (264)

> Sub-file of `.cursor/skills/pricing-wiring/SKILL.md`. Setting up policies, index rates and
> regions in any org (Help): `.cursor/skills/pricing-setup/price-revision-policies.md`.

How a **Price Revision Policy** changes a price in `RLM_DefaultPricingProcedure`, how CPI data is
seeded, and how to check a result. The figures here come from a fresh build with the quote procedure plan inactive [Measured: 2026-10-29, 264, org kind not recorded].

## What's involved

| Piece | Where |
|---|---|
| `IndexRate` (Region, Rate, `UsageType` Pricing, valid dates) | seeded by `datasets/sfdmu/qb/en-US/qb-price-revision/` |
| `Index_Rate_Decision_Table` (source `IndexRate`) | refreshed by `refresh_all_decision_tables` (`refresh_dt_default_pricing`) |
| `PriceRevisionPolicy` (`Flat` or `PriceIndex`, Formula, Region, effective dates) | the same plan |
| Renewal step `AdjustNetUnitPriceandSubtotalbyusingpricerevision` | `RLM_DefaultPricingProcedure` |
| Ramp step `Uplift` (a PriceRevision element) | `RLM_DefaultPricingProcedure` |

The renewal step's run conditions, formula terms, per-lot behavior and the CPI-on-ramps fallback are element
facts: [`../pricing-procedures/elements/price-revision.md`](../pricing-procedures/elements/price-revision.md)
-> *Renewal step in RLM_DefaultPricingProcedure*.

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
3. **Ramps: don't use CPI.** Help doesn't support a CPI policy on ramped products (see below). For a
   ramp uplift, use segment uplifts with Standard or Compound and a Flat policy (measured). A
   ramp uplift with no policy is not measured here; compounding with a Flat policy or no policy is
   what the platform allows [Core], but treat no policy as untested. See
   `ramped-quotes/SKILL.md` and `ramped-quotes/compound-uplift.md` (a SKU with CPI renewal uplift
   can't be used to verify a compound ramp).

## Expected results

| Case | Result |
|---|---|
| As-is renewal from 2027-05-01 of a 2,400 asset, `QB US CPI Plus Adjustment`, uplift 2 | **2,520** = 2,400 × (1 + 3% + 2%), the 2027 rate |
| Same renewal, `QB Flat Uplift`, uplift 2 | **2,448** |
| Compound group ramp, list 3,240, segment uplift 0 / 10 / 10, CPI policy | 3,337.20 / 3,654.72 / 3,648.24 (applied 3 / 12.8 / 12.6) |
| Same ramp, Flat policy | 3,240 / 3,564 / 3,920.40 (applied 0 / 10 / 21) |

CPI on ramps is a documented Help limitation; the CPI ramp row above is the fallback (each segment gets its
own year's rate plus its uplift, no compounding), not a supported demo path (see the element file).

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
- **Region, overlap, stale table.** See [`../pricing-setup/price-revision-policies.md`](../pricing-setup/price-revision-policies.md) -> *Troubleshooting*.
