# Mapping a Change Policy

Read this when a source (a contract, a quoting workbook, a PRD) states how changes after
the sale work. Parent: [asset-lifecycle-changes](SKILL.md).

| Source rule | Platform action | What decides the numbers | Verify |
|---|---|---|---|
| "Additions are co-termed and prorated by months remaining" | Amendment (`initiateAmendment`, `quantityChange` > 0) on the top-level asset. The amendment keeps the subscription end date, so the new units end with the original term [Help: `ind.qocal_amend_assets`], unless you use the separate feature that changes termed assets' end dates [Help: `ind.qocal_amend_and_renew_with_new_end_date`] | Proration in the pricing procedure (`pricing-procedures` → `elements/proration-and-subscription.md`) | Value = qty × unit price (from the asset's `PricingSource`, below) × the term count. The Default Proration Policy that `qb-pcm` ships counted whole annual periods plus the partial one by days (an add 184 days before a period's end: 2 + 184/365 with two whole periods left), so months remaining ÷ 12 matches only on an anniversary [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org]; for evergreen, check what the quote counts |
| "Volume bands apply to the new total; new units get the new band, existing units keep theirs" | Amendment | Volume and tier discount on the amendment line: does it see the new total or only the delta? | On assets with `PricingSource` `LastTransaction`, added units took the asset's last net price, existing units kept theirs, and nothing re-banded to the new total: the procedure's last-transaction branch ran, with no volume-band step, and a manual `Discount` on the line was ignored [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org]. The shipped default procedure has the same branch (`Calculateitemnettotalpriceforlineswithlasttransactionpricing`) [Repo: `force-app/main/default/expressionSetDefinition/RLM_DefaultPricingProcedure.expressionSetDefinition-meta.xml`]. `PricingSource` isn't writable through Place. How to re-band added units on an amendment is **Open** |
| "Swap plan A for plan B" | Swap (`/revenue/transaction-management/assets/actions/swap`), or an amendment that removes A and adds B | Each side's price; constraints between them | Run with configuration rules on; a constraint may force an order between changes |
| "Move part of a bundle component to another plan" (for example, some sites from one support plan to another), or "change a component's price" | Amendment of the top-level asset (Quick Rule 3). A plan held as an attribute: an attribute amendment, processed as a cancel and reprice from the amendment date [Help: `ind.qocal_fdo_examples_of_amendment_types_and_results`]. A price: a price amendment, delta quantity zero, a prorated credit for the old price and a charge for the new one; it works on bundles [Help: `ind.qocal_field_and_pricing_amendments`, `ind.qocal_field_and_price_amend_important_considerations`], and the repo turns Sales Price Amendments on [Repo: `unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml`]. Plans held as separate component products: remove one and add the other on the root's amendment (last row). A swap of the component asset is a separate route, undocumented for components | Whether the component's line takes the change. Help's attribute amendment sets one new value on the line, and doesn't describe changing part of a line's quantity. The swap request takes a quantity per outgoing asset [Dev guide: `connect_requests_initiate_swap_input`], and Billing lists partial-quantity swaps [Help: `ind.billing_view_billing_sched_group`], but no snapshot article says a swap takes a component asset | A price: a new `UnitPrice` on the component line of a root amendment worked: Amend / FieldAmendment, delta 0, a credit row per earlier lot at the old price and a charge for the full quantity at the new one, a new state period MRR after activation [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org]. A price decrease fails while estimated tax is on [Repo: `unpackaged/post_quote_est_tax_settings/settings/IncludeEstTaxInQuoteCPQ.settings-meta.xml`]. A plan held as a root answer: changing the answer moved all of the component's units to the other plan. Part of the units (−n on one plan's line, a new +n line for the other): refused by the model's one-plan rule, and with rules off by a component group allowing one component, whose Warning-level validation log still blocked the order [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org]. A plan held as an attribute on the component's line, and a swap of the component asset: **Open** |
| "Downgrades must still obey sizing rules" | Amendment or swap, with configuration rules on | CML constraints evaluated on the amendment | The rejection's own message |
| "Cancellations and reductions are credited for the months remaining" | Cancellation (`initiateCancellation`) on the top-level asset; a reduction is an amendment with `quantityChange` < 0, priced from prior sale prices, last in first out [Help: `ind.qocal_amend_assets`] | Selling model of each line, and billing | Cancellation on the quote: one-time = full price; evergreen = one period [Measured: 2026-11-05, 264]. A Term Defined reduction to 0 on a root amendment: −qty × net unit × the remaining term count, the partial period counted by days (row 1) [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org]. A Term Defined `initiateCancellation`, and evergreen reductions and swaps: **Open**. Backdated Term Defined reductions and cancellations were measured at invoice level [Repo: `rlm-business-apis/backdated-asset-lifecycle.md`]. Compare an evergreen line through its term count (Questions to settle in the plan) |
| "Renew for a new term at current net price plus N%" | Renewal (`initiateRenewal`); uplift through a price revision policy | Term Defined lines (a one-time line renews at quantity 0, Quick Rule 5); the asset's `PricingSource` (below) | The renewal quote's value per line, read from the detail rows. A price revision policy and `UnitPriceUplift` set on the new-sale lines reached the asset and the renewal with no edit to the renewal lines. A new-sale line with `SubscriptionTerm` 3 Annual still gave the asset a `RenewalTerm` of 1 Annual, so a multi-year renewal needs `renewalEndDate` [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org] |
| "Evergreen support carries on through the renewal" | Renewal (`initiateRenewal`) with the evergreen asset on it | Help covers only the edges: no renewal price uplift on evergreen assets [Help: `ind.qocal_consumer_price_index_and_uplifts_important_considerations`], no end-date change [Help: `ind.qocal_amend_and_renew_with_new_end_date`]; an evergreen asset has no lifecycle end date [Dev guide: `sforce_api_objects_asset`]; Billing treats a future-dated renewal of an evergreen product as an amendment [Help: `ind.billing_view_billing_sched_group`] | In a Term Defined bundle's renewal the evergreen component was a "No Change" line at quantity 0 and its asset was untouched [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org] (Quick Rule 5). A standalone evergreen asset's renewal: **Open** ([verification.md](verification.md) → Open) |
| "Escalate N% each year" | Group ramp with uplift (`ramped-quotes`) | Segment uplift | Amending a ramped bundle with one-time or evergreen children fails when built by API |
| "Remove a component but keep the bundle" | Cancelling the component alone is refused; an amendment of the top-level asset with the component's line at −n removes it (Quick Rule 3) | Model choice; the credit follows the component's selling model | On a Term Defined component: the component asset keeps a 0 state period from the amendment date, a "Change / Downsells" action, and the credit in last-in-first-out detail rows [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org]. An evergreen component's removal credit: **Open** |

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

### Changes dated at or after the term end

What Help says about changes near a Term Defined asset's end date:

- An amendment keeps the subscription end date [Help: `ind.qocal_amend_assets`]. Changing
  the end date is its own term-change amendment: the last transaction before the asset
  expires, not combined with another amendment, renewal or cancellation [Help:
  `ind.qocal_amend_renew_end_date_important_considerations`].
- An expired asset can't be swapped [Help:
  `ind.qocal_swap_upgrade_downgrade_important_considerations`]. It renews with Override
  Renewal Term and a start date on or after its lifecycle end date; a gap gets a
  zero-quantity asset state period [Help: `ind.qocal_renew_expired_assets`]. Without a
  start date the renewal was refused [Repo: `rlm-business-apis/backdated-asset-lifecycle.md`
  → Gotchas].
- A change in an asset's only or last state period is a regular amend, renew or cancel
  [Help: `ind.qocal_future_dated_order_amendments`].
- On a contract with cotermination, amendment and renewal line end dates follow the
  contract's end date [Help: `ind.qocal_coterminate_with_contract_end_date`].
- An evergreen asset has no lifecycle end date [Dev guide: `sforce_api_objects_asset`], and
  its end date can't be changed [Help: `ind.qocal_amend_and_renew_with_new_end_date`].

What the repo records:

- The amend date window, measured on group-ramped bundles on one 264 org with Quote
  output: on or after the Lifecycle Start Date of every asset in the request, and before
  the Lifecycle End Date of each asset that has one. The upper bound for assets with no end
  date wasn't measured. An asset with a future ramped renewal refused an earlier amend, and
  an ordered plain renewal blocked it the same way [Repo:
  `ramped-quotes/bundle-children-lifecycle.md` → Amend date window].
- Ordering a ramped renewal of a term-only ramped asset extended the same asset and its
  state periods in place [Repo: `ramped-quotes/bundle-children-lifecycle.md` → Renewal].
- Amend ±1 and cancel dated one and two months into a term made by an earlier ramped
  renewal passed, and renewals of expired plain and ramped assets are in the same file's
  measured results [Repo: `rlm-business-apis/backdated-asset-lifecycle.md`].

Measured outside group ramps, on a Term Defined bundle [Measured: 2026-11-11, 264, fresh
`ent-sb0` scratch org]:

- A plain renewal extended the same root and Term Defined component assets in place, as
  the ramped renewal above did (Quick Rule 5).
- An amendment dated exactly on a renewal's start date was accepted after that renewal was
  ordered and activated. It was a price amendment on an evergreen component's line.
- An amendment dated the same day as an earlier, already activated amendment was accepted.

Whether the date window holds outside group-ramped bundles, and its upper bound for assets
with no end date, are **Open** ([verification.md](verification.md) → Open).

## Questions to settle in the plan

- Which lines are bundle components, and must any be changeable on their own?
- Does a growing count (sites, users) live in the bundle root's quantity or in a root
  attribute that sizes the children? An amendment's `quantityChange` moves only the quantity;
  changing the answer on the amendment re-derives the children, and can reset the other
  answers (Quick Rules 2 and 3).
- Which selling model does each line use? That decides renewals and credits.
- Does the source state an evergreen line's values over a term (a total credit over the
  remaining term)? The quote counts an evergreen line for a pricing term count, not the
  term. Salesforce Pricing Setup's Evergreen default sets it: at 1 the price is one billing
  period; blank, it comes from the line's dates [Help: `ind.pricing_configure_proration_settings`].
  The shipped default procedure also assigns a constant count of 1 on its step for
  evergreen lines with non-prorated pricing [Repo:
  `force-app/main/default/expressionSetDefinition/RLM_DefaultPricingProcedure.expressionSetDefinition-meta.xml`].
  Which one gave the measured one-period credit wasn't traced. Before comparing, divide the
  source's total by its period count and multiply by the count the quote uses.
- Do changes run at the asset's last price, or at the current list price? The asset's
  `PricingSource` (`LastTransaction` or `PriceBookListPrice`) decides this when amending or
  renewing [Dev guide: `sforce_api_objects_asset`]. Two Help rules qualify it: a negative
  amendment is priced from prior sale prices, last in first out [Help: `ind.qocal_amend_assets`],
  and a list-price source drops the renewal uplift
  [Help: `ind.qocal_consumer_price_index_and_uplifts_important_considerations`]. Check which
  value the build's assets carry before comparing numbers. Every asset of the measured new
  sales read `LastTransaction`, so added units took the last net price with no re-band (the
  volume-band row above) [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org].
- Are changes backdated? If so, also read `rlm-business-apis` → `backdated-asset-lifecycle.md`.
