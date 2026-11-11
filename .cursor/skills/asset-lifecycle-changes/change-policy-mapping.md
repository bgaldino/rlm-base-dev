# Mapping a Change Policy

Read this when a source (a contract, a quoting workbook, a PRD) states how changes after
the sale work. Parent: [asset-lifecycle-changes](SKILL.md).

| Source rule | Platform action | What decides the numbers | Verify |
|---|---|---|---|
| "Additions are co-termed and prorated by months remaining" | Amendment (`initiateAmendment`, `quantityChange` > 0) on the top-level asset. The amendment keeps the subscription end date, so the new units end with the original term [Help: `ind.qocal_amend_assets`], unless you use the separate feature that changes termed assets' end dates [Help: `ind.qocal_amend_and_renew_with_new_end_date`] | Proration in the pricing procedure (`pricing-procedures` → `elements/proration-and-subscription.md`) | Value = qty × unit price (from the asset's `PricingSource`, below) × months remaining ÷ 12 for annual terms; for evergreen, check what the quote counts |
| "Volume bands apply to the new total; new units get the new band, existing units keep theirs" | Amendment | Volume and tier discount on the amendment line: does it see the new total or only the delta? | **Open**: measure on the product's tiers before promising it |
| "Swap plan A for plan B" | Swap (`/revenue/transaction-management/assets/actions/swap`), or an amendment that removes A and adds B | Each side's price; constraints between them | Run with configuration rules on; a constraint may force an order between changes |
| "Downgrades must still obey sizing rules" | Amendment or swap, with configuration rules on | CML constraints evaluated on the amendment | The rejection's own message |
| "Cancellations are credited for the months remaining" | Cancellation (`initiateCancellation`) on the top-level asset | Selling model of each line, and billing | On the quote: one-time = full price; evergreen = one period [Measured: 2026-11-05, 264]. Term Defined: **Open** |
| "Renew for a new term at current net price plus N%" | Renewal (`initiateRenewal`); uplift through a price revision policy | Term Defined lines only; one-time and evergreen lines renew at quantity 0 | The renewal quote's value per line, read from the detail rows |
| "Escalate N% each year" | Group ramp with uplift (`ramped-quotes`) | Segment uplift | Amending a ramped bundle with one-time or evergreen children fails when built by API |
| "Remove a component but keep the bundle" | Cancelling the component alone is refused (Quick Rule 3); removing it through an amendment of the top-level asset | Model choice | **Open**: removal through an amendment is unmeasured; measure it or sell the component as its own line |

## Questions to settle in the plan

- Which lines are bundle components, and must any be changeable on their own?
- Which selling model does each line use? That decides renewals and credits.
- Do changes run at the asset's last price, or at the current list price? The asset's
  `PricingSource` picks one: `LastTransaction` or `PriceBookListPrice`
  [Dev guide: `sforce_api_objects_asset`]. Help scopes it to positive-quantity amendments;
  a negative amendment is priced from prior sale prices, last in first out
  [Help: `ind.qocal_amend_assets`]. Map a source that prices additions "at standard pricing"
  to `PriceBookListPrice`, and check which value the build's assets carry before comparing
  numbers.
- Are changes backdated? If so, also read `rlm-business-apis` → `backdated-asset-lifecycle.md`.
