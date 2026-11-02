# Ramped Quotes — Compound price uplift

> Sub-file of `.cursor/skills/ramped-quotes/SKILL.md`.

Compound uplift makes each period's price uplift on the **prior period's factor**
(not the list price). Working in **percent units** (the units `UnitPriceUplift` and
`ApplUnitPriceUpliftPct` carry):
`applied%(n) = [(1 + applied%(n−1)/100) × (1 + unitUplift%(n)/100) − 1] × 100`,
and `NetUnitPrice(n) = base × (1 + applied%(n)/100)`. The `× 100` converts the
compounded multiplier back to a percentage — e.g. uplifts 5% then 3% give
`applied% = 8.15` (not `0.0815`), so `NetUnitPrice = base × 1.0815`. The first
period is the baseline; a 0% period is a *carryover* (prior cumulative multiplier
preserved).

It needs **all** of:

1. **Revenue Settings → Advanced Detail Line Pricing = ON** — this repo now defaults it
   **ON** (`unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml`,
   `enableAdvancedDetailLinePricing=true`; kept in sync across every scratch-def), so
   compound **is** available out of the box (the Compound option is hidden from the Ramp
   Uplift Type picklist only when ADLP is off). The 264 Help (*Compound Uplift for Ramp
   Deals*, `docs/salesforce/264/help/articles/ind.qocal_ramp_deal_compound_uplift.htm.md`)
   describes a hand-authoring path — clone the latest template, add a map line item
   `ItemApplUnitPriceUpliftPct__std` → `itemDetailApplUnitPriceUpliftPct__std`, then sync
   the context — but **none of that is required here**: the tracked
   `RLM_DefaultPricingProcedure` already carries the ramp-path compound `PriceRevision`
   (see prerequisite 4), and the bound ramp attributes plus the `itemDetailApplUnitPriceUpliftPct__std`
   target are **standard/inherited** from base `SalesTransactionContext` (present on the
   live `RLM_SalesTransactionContext`), so **no clone, no map line, and no context sync**
   is needed — verified on a fresh 264 build. Turning ADLP off *after* compound
   quotes/orders/assets exist still corrupts pricing/amendments/renewals. See
   `.cursor/skills/context-service/SKILL.md`.
2. **A group ramp** (this skill) — line ramps can't compound.
3. **`RampUpliftType='Compound'` on the ramp group** — the top-level
   `RampScheduleGroup` in multi-schedule mode (repo default), the single segment
   group when off; it cascades to segment subgroups and lines (SKILL.md → Quick Rule 5).
4. **A fully-configured ramp `PriceRevision` element** — the flag alone is *not*
   enough. **Enable Compound Uplift** (`IsCompoundUpliftEnabled=true`) appears only
   after a **lookup table** is selected, and requires bindings for **Ramp Identifier**,
   **Base Price Multiplier** (blank ⇒ 1 for new sale; prior compounded multiplier for
   amend/renew), **Uplift Method** (blank ⇒ silently *standard*, no compounding),
   and **Effective From**/**Effective To** — every segment needs a **unique Effective
   From** or pricing fails for the *entire* ramp group. This is *engine* setup —
   author/inspect it via `.cursor/skills/expression-sets/SKILL.md` →
   [Compound ramp uplift](../expression-sets/SKILL.md#compound-ramp-uplift). The tracked
   `RLM_DefaultPricingProcedure` **now carries this ramp-path compound `PriceRevision`**
   (`IsCompoundUpliftEnabled=true`) directly — the ramp branch
   (`Applyupliftstorampedsubscriptionsitemsduringamendment`, seq 2) was migrated from the
   old `FormulaBasedPricing` `Uplift` BKM by metadata deploy, so it works out of the box
   with no procedure clone. (The 264 Help's "newly-created procedure required" caveat is a
   **UI-authoring** limitation — you can't toggle Enable Compound Uplift on an existing
   procedure in the builder; deploying the full expression set metadata bypasses it, which
   is how the repo ships it.)
5. **`UnitPriceUplift` (per-period %) set per segment** on each `QuoteLineItem`.

**Unsupported for compound** (264 Help, *Considerations for Ramp Deals*,
`docs/salesforce/264/help/articles/ind.qocal_considerations_ramp_deals.htm.md`):
a SKU using **CPI renewal uplift**, **usage-based pricing**, or **derived pricing**
can't compound — don't build a compound ramp on one; its verification would be
invalid. Also: compound **resets on renewal** (Year 1 of the new term is the new
baseline), and records created **before Winter '27** use standard uplift.

Verify numerically by reading back the segments (SKILL.md → *Read-back → the ramp schedule*).
