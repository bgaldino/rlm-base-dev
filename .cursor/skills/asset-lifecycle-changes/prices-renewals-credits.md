# Asset Lifecycle Changes — Where prices land, renewals and credits

> Sub-file of `.cursor/skills/asset-lifecycle-changes/SKILL.md`. Full detail for Quick Rules 4, 5 and 6: detail rows, per-lot renewals, in-place renewal of Term Defined bundles, and credits by selling model.
> The numbered rules keep the numbers SKILL.md's Quick Rules cite.

## Rule 4: where the price lands

4. **Know where the price lands.**
    - On a renewal, a cancellation or a negative amendment, the unit price moves to
      `QuoteLineDetail` / `OrderItemDetail` rows, and the parent line's `UnitPrice` is null
      [Repo: `rlm-business-apis/SKILL.md`].
    - A pricing group keyed on net unit price admitted a reduction line, whose stored parent
      price is null, and its full-term value matched the expected value [Measured: 2026-11-12,
      264, scratch, one org]; that the net unit price is read from the pricing context is `[inferred]`. A per-lot renewal line
      has no net unit price at all: its prices sit on the per-lot detail rows, so such a group
      does not admit it ([../pricing-setup/scenarios/full-term-value.md](../pricing-setup/scenarios/full-term-value.md)).
      A quote-level full-term roll-up built on such groups read 0 on a per-lot renewal quote,
      while the quote's `GrandTotal` held the per-lot total and equalled the order's
      `TotalAmount` [Measured: 2026-11-17, 264, fresh `ent-sb0` scratch org]. Read a renewal's
      value from `GrandTotal` or the detail rows, not from a line-level roll-up.
    - A positive API amendment keeps the price on the parent.
    - A positive amendment edited in the UI also moved its price to detail rows (+2 and −1
      at the unit price) [Measured: 2026-11-05, 264].
    - A reduction's detail rows came one per earlier lot it drew from, last in, first out.
      A renewal priced each lot on its own row [Measured: 2026-11-11, 264, fresh `ent-sb0`
      scratch org].
    - **Why LIFO.** Lots are ordered by action date descending, then start date descending,
      positive before negative, then line number. A negative amendment walks them and writes
      one negative detail row per lot, for the smaller of the lot's quantity and what's left
      to remove, priced from that lot's own price: the credit is each lot's price, not
      today's, and not a blended one. The walk covers the unexpired lots. What a full removal
      leaves on the asset (a 0 state period was measured, above) wasn't traced [Platform
      behaviour, traced in part].
    - **Why per lot on a renewal.** A renewal at the last negotiated price gets one positive
      detail row per prior positive lot, each priced from its own lot, and its quantity is the
      latest period's quantity. That needs the `enableAsIsRenewals` setting on, a
      last-transaction pricing source, no ramp, no derived-price product, no attribute
      or price change on the line, and not an early renewal; otherwise it leaves this path. A non-ramped early renewal of a Term Defined line is repriced as a
      cancel-and-add pair of detail rows [Platform behaviour, traced]; a non-termed (evergreen)
      line takes its own branch first, which wasn't traced. A renewal on a price book list-price source is
      one line on the combined quantity (below). A ramped renewal leaves the per-lot path; one that
      isn't early is repriced as a single line [Platform behaviour, traced]. An early ramped
      renewal takes its own branch, which wasn't traced. Whether a renewal with an
      attribute or price change, or of a derived-price product, gets cancel-and-add rows or a
      single line isn't settled [Platform behaviour, traced in part]. The
      last-negotiated method copies the net unit price and has no volume-band step, so it
      doesn't re-band; a re-band needs an explicit pricing step, and only lines the step
      admits (renewal lines start at quantity 0) [Platform behaviour, traced]. A price
      revision policy applies to each lot's row separately, only when the renewal date falls
      inside the policy's validity window [Platform behaviour, traced].
    - **Measured on a bundle that grew by amendment.** A renewal of the root renewed each Term
      Defined lot on its own detail row at that lot's net price plus the uplift: the sale's
      lots, lots added by two later amendments, and a lot added at a re-banded price, which
      kept its band (no re-band on the combined quantity). The policy and `UnitPriceUplift`
      were set only on the new-sale lines; the amendment lines already carried them, inherited
      from the asset, with no edit. The renewal date was inside the policy's window, and every
      asset's `PricingSource` was `LastTransaction`. `enableAsIsRenewals` wasn't read on that
      org; the per-lot rows show the path ran [Measured: 2026-11-17, 264, fresh `ent-sb0`
      scratch org]. On the asset, a new
      sale copies the policy from the order line, and amend and renew periods inherit it from
      the current state period when the period's policy field is in the context definition, so an amend line doesn't reset it (without that field, not read); one step of that copy
      wasn't read [Platform behaviour, traced in part]. A renewal on an asset whose
      pricing source is the price book list price takes no per-lot path: it is one line on
      the combined quantity. Only when the asset's renewal pricing type is list price does it
      price from today's list price through the new-sale adjustment steps (bands expected on
      the total, tier arithmetic not traced or measured); with a blank or last-negotiated
      type it copies the prior net price and doesn't re-band. The two paths aren't the same
      switch: the method follows the renewal pricing type (blank counts as last
      negotiated), the per-lot path follows the pricing source [Platform behaviour, traced
      in part].
    - Read detail rows, or coalesce them, in anything that reports line prices.
## Rule 5: one-time lines have no term to renew; Term Defined bundles renew in place

5. **One-time lines have no term to renew; Term Defined bundles renew in place.**
    - Renewing a one-time product sets its quantity to zero [Help:
      `ind.qocal_asset_lifecycle_considerations`]. Renewing a one-time product with an
      evergreen component gave a $0 quote with quantity 0 on every line [Measured:
      2026-11-05, 264]. Model a renewable commitment with a Term Defined selling model.
    - A plain renewal of a Term Defined bundle extended the same assets in place: the root
      and its Term Defined components kept their asset records, their `LifecycleEndDate`
      moved to the renewal end, a new state period covered the renewal term, and the actions
      were "Change / Renewals". No new asset was created [Measured: 2026-11-11, 264, fresh
      `ent-sb0` scratch org].
    - In that renewal an evergreen component was a "No Change" line at quantity 0 with its
      per-period unit price, and its asset and open state period were untouched. A Term
      Defined component reduced to 0 earlier renewed at quantity 0, and its asset got a 0
      state period for the renewal term. It stays on the renewal as a Renew line at quantity
      0 and total 0, and its `LifecycleEndDate` moves to the renewal end, so assert "quantity
      0, value 0", not absence [Measured: 2026-11-17, 264, fresh `ent-sb0` scratch org].
      Standalone evergreen assets passed to a renewal
      request beside a Term Defined root came back as "No Change" lines at quantity 0, and
      their assets were untouched (no lifecycle end date, no new state period)
      [Measured: 2026-11-12, 264, scratch, one org]. To uplift them, send a price amendment (`quantityChange` 0, new `UnitPrice`)
      dated on the renewal start, after the renewal is activated; it was accepted on those
      standalone assets, with a new state period and a "Change / Upsells" action
      [Measured: 2026-11-12, 264, scratch, one org]. The same route uplifted Evergreen bundle
      components: a root amendment (`quantityChange` 0) dated on the renewal start, after the
      renewal activated, with the new `UnitPrice` on the component lines under configuration
      `Force` (Quick Rule 3), gave new state periods at the new price from that date
      [Measured: 2026-11-17, 264, fresh `ent-sb0` scratch org].
## Rule 6: credits follow the selling model

6. **On the quote, credits follow the selling model.** For one-time and evergreen lines
   the effective date didn't matter. At every date tested (+1, +30, +180, +300 and +400
   days):
    - cancelling a one-time product credited its full price;
    - an evergreen annual or monthly component credited exactly one period.
    - Both held on the Standard price book [Measured: 2026-11-05, 264].
    - A Term Defined component reduced to 0 through a root amendment credited quantity ×
      net unit price × the remaining term count. The Default Proration Policy that `qb-pcm`
      ships [Repo: `datasets/sfdmu/qb/en-US/qb-pcm/ProrationPolicy.csv`] counted whole annual periods left plus the days left in the current one ÷ that
      period's days (275/366 in a leap year), so a months-remaining figure matches only on
      an anniversary [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org] (day counts illustrative; the rule is what was measured). The count
      is the number of periods, with the first and last partial period counted as its days
      (inclusive, actual calendar days under the actual-days time period type) over the
      days in that full period, so a leap year changes the denominator (275/365 in a normal
      year, 275/366 in a leap year). The day counts above were first measured on contracts starting 1 January; a Term Defined cancel on a non-1-January start anchored periods on the **asset start** (-10,510.03 against a calendar-year -10,518.95) [Measured: 2026-11-26, 264, ent-sb0 harness build], see [cancel-swap-and-linking.md](cancel-swap-and-linking.md). A 30-day-month type counts 30 days a month. Not run: no such policy type was offered to create [Measured: 2026-11-12, 264, scratch, one org], so whether it reproduces a
      months-remaining source value on a mid-period start is unmeasured. A selling
      model's proration options take the policy only at create [read from the field describe, one org]. Turning
      partial periods off counts whole periods only. Read for the annual frequency with the
      actual-days type; that the first period runs to the calendar year end is inferred from
      the measured numbers, and other frequencies weren't read [Platform behaviour, traced
      in part]. A Term
      Defined top-level cancellation (`initiateCancellation`) and the invoice-level values
      are in [cancel-swap-and-linking.md](cancel-swap-and-linking.md); evergreen swap credits there too.
    - A reduction of a standalone Evergreen asset (`quantityChange` -4, illustrative) credited
      one period, in one last-in-first-out detail row and one monthly credit schedule per lot, and was
      ordered and activated, with a new state period at the reduced quantity
      [Measured: 2026-11-12, 264, scratch, one org; standalone asset, not a bundle
      component]. Help says an evergreen reduction takes units last in, first out
      from the current quantity, and a swap acts as an add plus a negative amendment [Help:
      `ind.qocal_fdo_examples_of_amendment_types_and_results`]; it doesn't say what either
      credits, and the reduction credit above is measured. A reduction of an Evergreen
      bundle component by 2 of 5 (one lot), ordered and activated through Skip plus a
      `QuoteAction` Amend edit (the test bundle lacked a required child, which `Skip` let through), gave a new state period at the reduced quantity and one credit
      schedule for the 2 [Measured: 2026-11-12, 264, scratch, one org]; read the state period, because
      `Asset.CurrentQuantity` still showed the old quantity after activation (unexplained).
      A reduction across two lots on a complete bundle, through `Force` with rules on, is
      measured too: a root answer change that moved part of an Evergreen monthly component's
      quantity to another component credited one period in one last-in-first-out detail row
      per lot (two rows), and added the other component as a new asset. It was ordered and
      activated, with state periods from the amendment date and quote values equal to the
      order's [Measured: 2026-11-17, 264, fresh `ent-sb0` scratch org]. Both lots had the
      same price, so a credit at each lot's own price isn't shown on a component. Evergreen swap and invoice credits: [cancel-swap-and-linking.md](cancel-swap-and-linking.md).
    - A source's term-total value for an evergreen line (a total credit over the remaining
      term) doesn't compare with the quote directly: the quote counts the line for its
      pricing term count, not the term ([change-policy-mapping.md](change-policy-mapping.md)
      → Questions to settle in the plan).
