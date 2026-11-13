# Price Revision — Compound ramp uplift

> Sub-file of [`price-revision.md`](price-revision.md) (the `PriceRevision` element). Release 264 /
> API v68.0. Sources: `ind.qocal_ramp_deal_compound_uplift.htm`,
> `ind.qocal_ramp_deal_compound_uplift_sales_reps.htm`, `ind.qocal_considerations_ramp_deals.htm`,
> `ind.pricing_use_the_price_revision_element_in_a_pricing_procedure.htm`; shipped XML
> `RLM_DefaultPricingProcedure`; core 264 re-read for the arithmetic and grouping. Engine runtime rules
> (grouping, error codes, per-segment math) are in [`price-revision.md` → Runtime behavior](price-revision.md#runtime-behavior-core).

Compound ramp uplift (each ramp segment's price uplifts on the *prior segment's* factor, not the
list price) is a **group-ramp + pricing-procedure** capability. The procedure element is the
`PriceRevision` step; the rest is Revenue Settings + a **group** ramp deal. It is **not** a line
field you set: `RampUpliftType` is read-only on `QuoteLineItem`/`OrderItem` (Place API, Apex and
Tooling all reject a write) and lives on the `QuoteLineGroup`, cascading to its ramped lines. [Repo]

**Five prerequisites** (Help: *Compound Uplift in Ramp Deals*, *Create Ramp Deals with Standard or
Compound Price Uplifts*):

1. **Revenue Settings -> Advanced Detail Line Pricing = ON.** This repo defaults it ON
   (`unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml`,
   `enableAdvancedDetailLinePricing=true`, kept in sync across every scratch-def); compound is hidden from the Ramp Uplift Type picklist
   only when ADLP is off. The 264 Help hand-authoring path (*Compound Uplift for Ramp Deals* ->
   *Use Advanced Transaction Detail Line Pricing to Map Custom Fields*: clone the template, add a
   map line item mapping `ItemApplUnitPriceUpliftPct__std` -> `itemDetailApplUnitPriceUpliftPct__std`,
   sync the context) is **not required in this repo**: tracked `RLM_DefaultPricingProcedure`
   already ships the ramp-path compound `PriceRevision` (prerequisite 4), and the bound ramp
   attributes plus the `itemDetailApplUnitPriceUpliftPct__std` target are standard/inherited from
   base `SalesTransactionContext`, so no clone, map line or context sync is needed
   [Live, 2026-10-28, fresh 264 build]. Off => standard (list-based) uplift only;
   turning it off *after* compound quotes/orders/assets exist corrupts pricing, amendments, renewals.
2. **Ramp Deals for *Groups*** (a group ramp; Revenue Settings *Ramp Deals for Groups in Quotes and Orders* on, and a *Default Ramp Uplift Type* of Standard or Compound that new schedules inherit and reps can override per schedule group [Help: `ind.qocal_ramp_deal_compound_uplift.htm`]), not the line-level ramp path. A single-line
   `createRampDeal` yields ungrouped segments (`QuoteLineGroupId=null`): no group to hold the
   uplift mode, so it can never compound.
3. **`RampUpliftType='Compound'` on the ramp group**: with *Multiple Ramp Schedules Per
   Transaction* on (repo default) set it on the **top-level `RampScheduleGroup`**; with it off, on
   the single ramp segment group. On individual segment groups and lines the type is read-only. It
   cascades to every ramped line in the schedule.
4. **A fully-configured ramp `PriceRevision` element.** `IsCompoundUpliftEnabled=true` (UI
   "Enable Compound Uplift") is *necessary but not sufficient*. Per Help (*Use the Price Revision
   Element in a Pricing Procedure*) the checkbox appears **only after a lookup table is selected**
   and exposes bindings that must all be set:

   | Binding | Rule (blank / wrong =>) |
   |---|---|
   | **Ramp Identifier** | Groups a ramp's segments so they compound independently; lines with no Ramp Identifier price independently [Help][Core] |
   | **Base Price Multiplier** | Blank => 1 for a new sale; for amend/renew, the ramp's compounded multiplier from the prior transaction [Help]. Passed as a percent (38.6 = 38.6%), read from the earliest segment only [Core] |
   | **Uplift Method** | **Blank => silently *standard* (no compounding)**: the quiet failure mode |
   | **Effective From** / **Effective To** | Segment date range; **every segment needs a *unique* Effective From**: a missing or duplicated one **fails pricing for the entire ramp group**, not just that segment |

   The 264 Help says compound "requires a newly-created procedure": a **UI-authoring**
   limitation (the builder won't enable compound uplift on an existing procedure); deploying the
   full expression-set metadata bypasses it [Live, 2026-10-28]. Tracked
   `RLM_DefaultPricingProcedure` **ships two** `PriceRevision` BKMs: the long-standing **non-ramp**
   step, and the **ramp-path** compound step (migrated from the old `FormulaBasedPricing` `Uplift`
   BKM by metadata deploy). Compound ramp uplift works on the tracked default out of the box; no
   clone is needed:

   | BKM step (parent filter), both seq 2 in their parent | Kind in tracked default | Drives |
   |---|---|---|
   | `AdjustNetUnitPriceandSubtotalbyusingpricerevision` under *Apply price revision for lines with subscription and without derived pricing* | `PriceRevision` (present) | non-ramp price revision |
   | `Uplift` under *Apply uplifts to ramped subscriptions items during amendment* (filter requires `IsLineGroupRamped__std=true` AND `ItemRampIdentifier IS NOT NULL`) | `PriceRevision` with `IsCompoundUpliftEnabled=true` (migrated from `FormulaBasedPricing`) | **compound** ramp uplift when `RampUpliftType=Compound`; flat when `Standard` |

   **Compared with the 264 template** (2026-10-28; a fresh "Revenue Management Default Pricing
   Procedure" saved from Expression Set Templates on a fresh 264 build) [Live, 2026-10-28]:
   - Every template element is present except **derived pricing**, which the repo omits by owner decision.
   - The ramp `Uplift` step matches the template's `PriceRevision` parameter for parameter. Its
     `Rate` output goes to `ItemConsumerPriceIndex__std` as in the template, rather than sharing
     `ItemApplUnitPriceUpliftPct__std` with `AppliedUnitPriceUplift`. That's for parity only: a
     group-ramp matrix priced identically before and after.
   - The ramp filter keeps three extra criteria on two fields (`ItemUnitPriceUplift__std
     IsNotNull`, `IsLineGroupRamped__std IsNotNull`, `IsLineGroupRamped__std = true`), which limit it
     to **group** ramps. Measured with the template's four criteria instead, line ramps took a
     standard uplift. But a Year-2 group-ramp amendment then priced 4,312.44 (3,564 x 1.21) instead
     of 3,564: the uplift went on again on top of the already-uplifted last transaction price. So
     keep the group gate; line ramps get no uplift here.

5. **`UnitPriceUplift` (per-year %) set per segment** (writeable). First segment is the baseline
   (applied uplift = its own line uplift, usually 0); a 0% segment is a *carryover* (prior
   cumulative multiplier preserved, not reset).

Compounding math (in **percent units**, matching `UnitPriceUplift` / `ApplUnitPriceUpliftPct`):
`applied%(n) = [(1 + applied%(n-1)/100) x (1 + unitUplift%(n)/100) - 1] x 100`, and
`NetUnitPrice(n) = base x (1 + applied%(n)/100)`. The `x 100` converts the compounded multiplier
back to a percentage: uplifts 5% then 3% give `applied% = 8.15` (not `0.0815`), i.e.
`NetUnitPrice = base x 1.0815`. [Live, 2026-10-28][Core: same multiplier arithmetic, seeded from `PreviousSegmentMultiplier` as a percent]

**The uplifted price is not rounded to the cent.** A compound segment's `NetUnitPrice` carried
more than two decimals (the base times the compounded multiplier, at full precision), and the line total followed it, so a
source that rounds each year's price to the cent missed by fractions of a cent per unit
[Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org]. For example, with 5% then 2%,
1,001.00 × 1.071 = 1,072.071, not 1,072.07. A rounding step that runs before the uplift, such as one before the
manual discounts, does not cover this. Add a second one after it: a List Group placed right after
the ramp uplift group (`Applyupliftstorampedsubscriptionsitemsduringamendment` in the shipped
default), filter `ItemRampIdentifier IsNotNull AND NetUnitPrice IsNotNull`, and a Formula-Based
Pricing step `ROUND(NetUnitPrice, 2)` → `NetUnitPrice`. It still runs before the term pricing
groups, so the line total follows the rounded price. Measured: each segment then matched its
cent-rounded value, and so did the line total. Element shapes:
[`formula-based-pricing.md`](formula-based-pricing.md),
[`list-group-and-list-operation.md`](list-group-and-list-operation.md),
[`rounding-values.md`](rounding-values.md).

A line also leaves the compound path (priced standard) when its `PolicyType` is anything but blank or Flat, so a Price Index line never compounds [Core]. A compound-intended line with a negative quantity is skipped (not priced) [Core].

**Unsupported for compound** (Help, *Considerations for Ramp Deals*; core enforces only the CPI/Price Index case, the others are Help-only): a SKU using **CPI renewal
uplift**, **usage-based pricing**, or **derived pricing** can't compound. Compound also **resets on
renewal** (new term's Year 1 is the new baseline); pre-Winter '27 records use standard uplift.

## Lifecycle and limits (Help)
All [Help: `ind.qocal_considerations_ramp_deals.htm`] unless noted.
- **Mode is fixed once assetized**: the type recorded on the asset state period cannot change;
  amendments and renewals inherit it per asset-sourced line (they may mix Standard and Compound lines;
  an initial sale has one type for all ramped lines). New ramped lines inherit the group's type.
- **Amendments**: the previous segment's uplift is the preceding asset state period in date order, which
  is what feeds *Base Price Multiplier*. On renewal the final segment's uplift becomes the renewal
  uplift while compounding restarts at the new Year 1 baseline.
- **Pricing impact**: changing the type on a schedule group reprices every segment and line. A compound
  schedule reprices every line in the group on each run (a standard one reprices only changed segments)
  [Help: `ind.qocal_ramp_deal_compound_uplift_sales_reps.htm`]. Delta pricing cannot be used with Dual
  Persistence mode [Help: `ind.qocal_use_delta_pricing_for_quotes_and_orders.htm`]; delta skipping applies when the setting is on and the save is a PATCH edit with System pricing, Dual Persistence mode off, a completed calculation status (Completed with Pricing or with Tax) and no validation errors [Platform behaviour, traced]; further conditions (the transaction's update tracking) also apply, so treat this list as partial, and otherwise every line reruns ([runtime](../runtime-and-observability.md)).
- **Ramp limits**: up to 12 group ramp segments per schedule, 10 ramp schedule groups per transaction
  (Multiple Ramp Schedules on), 10 segments per line ramp; group and line ramps can't share a quote or
  order; derived-pricing products in a group ramp don't price correctly; ramped line items support GMT
  only; usage-based assets allow cloning segments but not date changes in amendments.
- **Settings and permissions**: Revenue Settings needs *Customize Application*; setting the type on a
  quote line group needs *Create on Quotes* (orders: *Create on Orders*). Sync the context definition
  before using compound (the repo's tracked build did not need a manual sync, see prerequisite 1).
- **Renewal uplifts (non-ramp)**: apply only to term-defined products; the uplift is a Formula-Based
  Pricing calculation (consistent with the shipped `FormulaBasedPricing` Uplift in the PRM and Recalc
  procedures); apply uplifts after discounts under Last Transaction Pricing; the asset's Pricing Source
  must be Last Transaction Pricing, and a list-price source ignores the uplift. One-time and evergreen
  assets, usage-based and derived-pricing products don't support uplifts
  [Help: `ind.qocal_renewal_price_uplifts.htm`, `ind.qocal_consumer_price_index_and_uplifts_important_considerations.htm`].
