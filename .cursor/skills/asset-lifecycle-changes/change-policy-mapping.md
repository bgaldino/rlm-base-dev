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
| "Renew for a new term at current net price plus N%" | Renewal (`initiateRenewal`); uplift through a price revision policy | Term Defined lines (a one-time line renews at quantity 0, Quick Rule 5); the asset's `PricingSource` (below) | The renewal quote's value per line, read from the detail rows |
| "Evergreen support carries on through the renewal" | Renewal (`initiateRenewal`) with the evergreen asset on it | Help covers only the edges: no renewal price uplift on evergreen assets [Help: `ind.qocal_consumer_price_index_and_uplifts_important_considerations`], no end-date change [Help: `ind.qocal_amend_and_renew_with_new_end_date`]; an evergreen asset has no lifecycle end date [Dev guide: `sforce_api_objects_asset`]; Billing treats a future-dated renewal of an evergreen product as an amendment [Help: `ind.billing_view_billing_sched_group`] | **Open**: Help doesn't say what the renewal quote does to an evergreen line ([verification.md](verification.md) → Open). Quick Rule 5 has the bundle case |
| "Escalate N% each year" | Group ramp with uplift (`ramped-quotes`) | Segment uplift | Amending a ramped bundle with one-time or evergreen children fails when built by API |
| "Remove a component but keep the bundle" | Cancelling the component alone is refused (Quick Rule 3); removing it through an amendment of the top-level asset | Model choice | **Open**: removal through an amendment is unmeasured; measure it or sell the component as its own line |

## Replay the source's changes in date order

A source's change examples (for example contract changes C-1 to C-4 and a renewal R-1)
usually act on the same assets, so test them as one dated sequence on one build, not each
from a fresh asset. These Help rules constrain the order:

- You can't renew an asset that already has a future-dated renewal scheduled
  [Help: `ind.qocal_future_dated_order_amendments_important_considerations`].
- A renewal before the scheduled renewal date overrides all future asset state periods,
  amendments and renewals, and a cancellation leaves the asset in a terminal state with no
  further amend, renew or cancel [Help: `ind.qocal_fdo_examples_of_amendment_types_and_results`].

Help reads both ways on a change dated before one already scheduled. The amend and cancel
articles say that if an asset has a future-dated amend, renew or cancel transaction, you
can't initiate a transaction with an earlier start date [Help: `ind.qocal_amend_assets`,
`ind.qocal_cancel_assets`]. *Future-Dated Changes* says you can pick a date before an
existing future asset state period [Help: `ind.qocal_future_dated_order_amendments`], and
its examples add licenses on May 1 "even though you scheduled 5 more licenses for June 1"
[Help: `ind.qocal_fdo_examples_of_amendment_types_and_results`]. Which applies is **Open**
([verification.md](verification.md) → Open).

Run the examples in effective-date order, each through activation before the next; that
order is safe under either reading. Any example that can't run in that order (dated before
a change already applied, or after a cancellation or early renewal of the same asset)
becomes a decision for the plan: re-date it, give it its own asset, or drop it.

## Questions to settle in the plan

- Which lines are bundle components, and must any be changeable on their own?
- Does a growing count (sites, users) live in the bundle root's quantity or in a root
  attribute that sizes the children? An amendment's `quantityChange` moves only the quantity
  (Quick Rule 3).
- Which selling model does each line use? That decides renewals and credits.
- Do changes run at the asset's last price, or at the current list price? The asset's
  `PricingSource` (`LastTransaction` or `PriceBookListPrice`) decides this when amending or
  renewing [Dev guide: `sforce_api_objects_asset`]. Two Help rules qualify it: a negative
  amendment is priced from prior sale prices, last in first out [Help: `ind.qocal_amend_assets`],
  and a list-price source drops the renewal uplift
  [Help: `ind.qocal_consumer_price_index_and_uplifts_important_considerations`]. Check which
  value the build's assets carry before comparing numbers.
- Are changes backdated? If so, also read `rlm-business-apis` → `backdated-asset-lifecycle.md`.
