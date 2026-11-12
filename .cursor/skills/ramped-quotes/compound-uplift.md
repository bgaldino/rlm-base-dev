# Ramped Quotes — Compound price uplift

> Sub-file of `.cursor/skills/ramped-quotes/SKILL.md`.

Compound uplift makes each period's price uplift on the **prior period's factor**
(not the list price). The engine side (Advanced Detail Line Pricing, the ramp
`PriceRevision` element and its bindings, the compounding arithmetic, and the
SKUs that can't compound) is documented once, in
[`../pricing-procedures/elements/price-revision-compound-uplift.md`](../pricing-procedures/elements/price-revision-compound-uplift.md).
The repo's build turns ADLP on and ships the ramp-path compound `PriceRevision` in
`RLM_DefaultPricingProcedure`, so on a fresh build nothing in the engine needs changing.

On the **quote**, compound needs all of:

1. **A group ramp** (this skill). Line ramps can't compound: a single-line
   `createRampDeal` yields ungrouped segments with no group to hold the uplift mode.
2. **`RampUpliftType='Compound'` on the ramp group**: the top-level
   `RampScheduleGroup` in multi-schedule mode (repo default), the single segment
   group when off. It cascades to segment subgroups and lines (SKILL.md → Quick
   Rule 5); it is read-only on the lines themselves.
3. **`UnitPriceUplift` (per-period %) set per segment** on each `QuoteLineItem`.
   The first period is the baseline; a 0% period is a *carryover* (prior cumulative
   multiplier preserved).
4. **A SKU that can compound**: not one with CPI renewal uplift, usage-based
   pricing or derived pricing. Verifying a compound ramp on one of those is invalid.

Quick check for a read-back: uplifts 5% then 3% give `ApplUnitPriceUpliftPct = 8.15`
(percent units, not `0.0815`), so `NetUnitPrice = base × 1.0815`. The general
formula is in the element file above. Compound resets on renewal (Year 1 of the new
term is the new baseline).

**Precision: the uplift is not rounded.** `NetUnitPrice` and the line total carry the unrounded
product of the base and the factor (measured 2026-11-11, fresh 264 `ent-sb0` scratch org, UI group
ramp, uplift 0 / 3 / 3). For example a base of 1,234.00 at 6.09% reads 1,309.1506, and quantity 10
totals 13,091.506. Read-backs that expect cents won't match, and a source that rounds each year's
price to cents disagrees from segment 2 on. To match it, add a rounding step **after** the ramp uplift
(a list group on ramped lines that sets `NetUnitPrice` to `ROUND(NetUnitPrice, 2)`, placed after the
*Apply uplifts to ramped subscriptions items during amendment* step). A rounding step earlier in the
procedure runs before the uplift, so it can't round the uplift's result. With the step in place the
line total followed the rounded price.

Pitfalls that show up on the quote (details in the element file):

- Every segment needs a **unique Effective From** (start date). A missing or duplicated
  one fails pricing for the **whole ramp group**, not just that segment.
- A blank **Uplift Method** binding on the procedure silently gives standard
  (non-compound) uplift: each segment gets its own non-cumulative uplift, with no error.
- Turning ADLP off after compound quotes, orders or assets exist corrupts their
  pricing, amendments and renewals.
- Records created before Winter '27 use standard uplift.

Verify numerically by reading back the segments (SKILL.md → *Read-back → the ramp schedule*).
