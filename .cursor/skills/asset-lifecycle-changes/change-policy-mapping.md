# Mapping a Change Policy

Read this when a source (a contract, a quoting workbook, a PRD) states how changes after
the sale work. Parent: [asset-lifecycle-changes](SKILL.md).

| Source rule | Platform action | What decides the numbers | Verify |
|---|---|---|---|
| "Additions are co-termed and prorated by months remaining" | Amendment (`initiateAmendment`, `quantityChange` > 0) on the top-level asset. The amendment keeps the subscription end date, so the new units end with the original term [Help: `ind.qocal_amend_assets`], unless you use the separate feature that changes termed assets' end dates [Help: `ind.qocal_amend_and_renew_with_new_end_date`] | Proration in the pricing procedure (`pricing-procedures` → `elements/proration-and-subscription.md`) | Value = qty × unit price (from the asset's `PricingSource`, below) × months remaining ÷ 12 for annual terms; for evergreen, check what the quote counts |
| "Volume bands apply to the new total; new units get the new band, existing units keep theirs" | Amendment | Volume and tier discount on the amendment line: does it see the new total or only the delta? | **Open**: measure on the product's tiers before promising it |
| "Swap plan A for plan B" | Swap (`/revenue/transaction-management/assets/actions/swap`), or an amendment that removes A and adds B | Each side's price; constraints between them | Run with configuration rules on; a constraint may force an order between changes |
| "Move part of a bundle component to another plan" (10 sites from Premier to Standard support), or "change a component's price" | Amendment of the top-level asset (Quick Rule 3). A plan held as an attribute: an attribute amendment, processed as a cancel and reprice from the amendment date [Help: `ind.qocal_fdo_examples_of_amendment_types_and_results`]. A price: a price amendment, delta quantity zero, a prorated credit for the old price and a charge for the new one; it works on bundles [Help: `ind.qocal_field_and_pricing_amendments`, `ind.qocal_field_and_price_amend_important_considerations`], and the repo turns Sales Price Amendments on [Repo: `unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml`]. Plans held as separate component products: remove one and add the other on the root's amendment (last row). A swap of the component asset is a separate route, undocumented for components | Whether the component's line takes the change. Help's attribute amendment sets one new value on the line, and doesn't describe changing part of a line's quantity. The swap request takes a quantity per outgoing asset [Dev guide: `connect_requests_initiate_swap_input`], and Billing lists partial-quantity swaps [Help: `ind.billing_view_billing_sched_group`], but no snapshot article says a swap takes a component asset | **Open**: none of these paths is measured on a component. A price decrease fails while estimated tax is on [Repo: `unpackaged/post_quote_est_tax_settings/settings/IncludeEstTaxInQuoteCPQ.settings-meta.xml`]. If it must work on stage, sell the component as its own line |
| "Downgrades must still obey sizing rules" | Amendment or swap, with configuration rules on | CML constraints evaluated on the amendment | The rejection's own message |
| "Cancellations and reductions are credited for the months remaining" | Cancellation (`initiateCancellation`) on the top-level asset; a reduction is an amendment with `quantityChange` < 0, priced from prior sale prices, last in first out [Help: `ind.qocal_amend_assets`] | Selling model of each line, and billing | Cancellation on the quote: one-time = full price; evergreen = one period [Measured: 2026-11-05, 264]. Term Defined on the quote, and evergreen reductions and swaps: **Open**. Backdated Term Defined reductions and cancellations were measured at invoice level [Repo: `rlm-business-apis/backdated-asset-lifecycle.md`]. Compare an evergreen line through its term count (Questions to settle in the plan) |
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

### Changes dated at or after the term end

No snapshot article gives an amendment rule for a date at or after a Term Defined asset's
end date, or on its renewal date. What Help does say:

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

Measured: amend ±1 and cancel dated one and two months into a term made by an earlier
ramped renewal passed [Repo: `rlm-business-apis/backdated-asset-lifecycle.md` →
group-ramp assets]. That is the only measured shape for an amendment or cancellation after a
renewal: it runs after the renewal's activation, dated inside the new term. (Renewals dated
after a term end were measured too; same file, Measured results.) An amendment or
cancellation dated after the end of a term that wasn't renewed, and one dated on the
renewal start date itself, are **Open**
([verification.md](verification.md) → Open).

## Questions to settle in the plan

- Which lines are bundle components, and must any be changeable on their own?
- Does a growing count (sites, users) live in the bundle root's quantity or in a root
  attribute that sizes the children? An amendment's `quantityChange` moves only the quantity
  (Quick Rule 3).
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
  value the build's assets carry before comparing numbers.
- Are changes backdated? If so, also read `rlm-business-apis` → `backdated-asset-lifecycle.md`.
