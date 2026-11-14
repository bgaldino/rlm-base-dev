---
name: asset-lifecycle-changes
description: >-
  Model and verify what happens to sold assets in Revenue Cloud: amendments
  (add or remove quantity, co-termed), swaps, cancellations, renewals and
  rollbacks, and how a source's change policy (co-terming, re-banding, credits,
  renewal uplift) maps onto them. Covers where prices and attributes land on
  amendment, cancellation and renewal lines, bundle-component limits, credits by
  selling model, and a headless test that follows a change through reprice,
  order, activation and the asset. Use before promising lifecycle numbers in a
  demo or plan. Backdated changes and billing: rlm-business-apis →
  backdated-asset-lifecycle.md. Renewal test data: renewal-asset-creation.
---

# Asset Lifecycle Changes — Amend, Swap, Cancel, Renew

Use this skill when a model has to survive after the sale: a customer adds locations,
moves to a cheaper plan, cancels an add-on or renews at a new price. The domain
skills cover the individual APIs. This one covers the modeling decisions and the
behaviour you have to verify, because Help describes how to set lifecycle changes up but
not the numbers they produce. Claims are tagged `[Help: <article>]`, `[Dev guide: <article>]`,
`[Repo: <path>]` and `[Measured: <date>, 264]`. `[Platform behaviour, traced]` is a rule
read from the platform's own behaviour, not measured here; where it explains a measured
claim, both tags appear. `[Platform behaviour, traced in part]` is the same, but only the
mechanism was read; its scope, path or consequence isn't established. The 2026-11-05 runs were on QuantumBit
builds. The 2026-11-11 runs were on fresh 264 `ent-sb0` scratch orgs, on a bundle sized by
CML root answers, priced by a procedure cloned from the shipped default with overlays,
with configuration rules on ([verification.md](verification.md) → Measured
results, 2026-11-11).

## Quick Rules

1. **Decide each change type's numbers before you build, then test them past the first
   placement.** Follow the change from quote → reprice → order → reprice → activation →
   asset state periods → asset actions. A value that is right on the quote can still
   drift later ([verification.md](verification.md)).
    - **Never reprice a renewal quote after its order is activated; until measured, treat amendment
      and ramped quotes the same.** Pricing of a renewal, amendment or cancellation line reads the
      source asset's current state, and activation changes that state, so the rule covers all three
      [Platform behaviour, traced in part]. Measured once on a renewal quote: a full reprice (every
      line, pricing `Force`, configuration `Skip`) after the order was activated set the renewal
      lines' totals and the quote total to 0 [Measured: 2026-11-12, 264, scratch, one org] — each
      lot became a −lot/+lot pair netting 0, and the order and assets were unchanged. Not measured
      on amendments or ramped quotes; why the reprice returned 0 is not traced. Read quote values
      before activation and don't reprice afterwards.
2. **Read attributes as well as prices.** A quantity change on an amendment line, placed
   with configuration rules on (the UI's inline quantity edit does this), resets the
   line's attributes to the product defaults. Activation keeps them on the asset, and the
   next amendment inherits them. The price stays right [Measured: 2026-11-05, 264]. Add
   quantity with `initiateAmendment` and `quantityChange`, which kept them.
    - **Changing one CML answer on an amendment reset the others.** When a Place request on
      an amendment quote changed one root answer with rules on, every answer the request
      didn't change went back to its CML default on the solve, and the children those
      answers size came back as delta lines toward the defaults (negative in the measured
      runs, where the answers were above their defaults). Re-sending an answer at its current
      value didn't protect it: Place drops an unchanged value. A change to lines only, with
      no answer in the request, kept every answer [Measured: 2026-11-11, 264, fresh `ent-sb0`
      scratch org].
    - **Why:** the repo's quote-line trigger gives each amendment line the configurator node
      status from its source asset's latest asset action (by `ActionDate`), read from that
      action's source rows (`AssetActionSource.RLM_ConstraintEngineNodeStatus__c`) [Repo:
      `unpackaged/post_constraints/triggers/RLM_QuoteItemTrigger.trigger`]. The node status
      records which answers the user set, not their values; with none on the root line, a
      solve that changes an answer treats every answer the request doesn't change as a
      default. An answer edit keeps the other answers only when those rows carry it.
      Activation fills them only when the context definition has an order-to-asset rule
      (`AssetActionSource` ⇐ `SalesTransactionItem` in `AssetToSalesTransactionMapping`), and
      never fills rows made from order product detail rows: the cancel-and-reprice pair an
      answer-change amendment writes on the root [Measured: 2026-11-11, 264, scratch org].
    - **Why detail rows stay blank.** Activation writes one asset action source row per
      order line, or one per order line detail when the line has details; a detail-sourced
      row takes its quantity and prices from the detail, and its `ReferenceEntityItemId` is
      the detail's Id. Nothing in activation writes node status. A custom field reaches
      these rows only through the order-to-asset custom-field mapping: an item-sourced row
      reads the mapped tags on the line's node, a detail-sourced row reads only the mapped
      tags on the detail's own node. A rule mapping from the line therefore fills item rows
      and leaves detail rows blank, and no native step copies status from line to detail.
      This holds for any mapped custom tag, not just node status [Platform behaviour,
      traced]. An answer-change amendment reprices the line as a cancel-and-add pair, and the
      next amendment copies the saved status from the first row of the selected
      action-source set (the filtered set for an attribute-change amendment, all rows sorted
      by date for a normal renew); if that row is a detail-sourced row with no status, the status is
      blank and the answers reset. Which row sorts first wasn't verified [Platform behaviour,
      traced in part]. One measurement conflicts: on one org the field was empty on every
      row, item-sourced ones included, while the order line's was filled (verification.md).
      The trace expects item rows to fill when the rule exists, so the cause (detail rows
      only, a different field name, the rule or tag absent) isn't established: **Open**, a
      live check.
    - So the repo ships both halves: the
      rule in its context plan [Repo: `datasets/context_plans/ConstraintEngineNodeStatus`],
      and a before-insert trigger that fills a blank row from its order product, directly
      or through the detail row [Repo:
      `unpackaged/post_constraints/triggers/RLM_AssetActionSourceTrigger.trigger`]. With
      both, answers held through two answer-change amendments in a row on a fresh build
      [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org].
      Configurator side: `constraint-models` → `quantities-from-attributes.md` → open item 12.
    - **Check and work around.** After every activation in a multi-step replay, read the
      root's latest asset action source rows (verification.md step 6). Where they're blank,
      either restate every answer that differs from its CML default (in a second Place
      request after the reset, where it counts as a change), or before amending copy each
      row's node status from its order product (`ReferenceEntityItemId`, directly or
      through the detail row's `OrderItemId`). The reference item may be the order line or its detail row, and the
      platform doesn't copy node status between line-sourced and detail-sourced rows
      [Platform behaviour, traced]. Blank rows are expected on an org built
      before the rule and trigger shipped, and on assets activated before they were
      deployed: the trigger acts only on new rows. Read every line's delta before ordering.
3. **Amend, renew and cancel act on top-level assets.** Help's amend, renew and cancel
   procedures each say to select a bundle's parent asset, not the child [Help:
   `ind.qocal_amend_assets`, `ind.qocal_renew_assets`, `ind.qocal_cancel_assets`].
   Cancelling or renewing a bundle component alone is refused: "the asset is a bundle
   component. Provide the top-level asset" [Measured: 2026-11-05, 264].
    - **Removing a Term Defined component through an amendment of the top-level asset
      works.** Amend the root with `quantityChange` 0, then set the component line's `Quantity` to −n with a
      Place request, rules on. On an amendment quote `Quantity` is the delta, and
      `StartQuantity` and `EndQuantity` are the totals before and after. The component asset
      stays, with a 0 state period from the amendment date, a "Change / Downsells" action, and
      the credit in detail rows [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org]. Only
      a Term Defined component was removed; an evergreen component's credit on removal to 0 is
      **Open**; a partial reduction (one lot) is measured (Quick Rule 6). A component that must be cancelled on its own, into a terminal state, still has to be
      sold as its own line.
    - `quantityChange` is the quantity to add to or reduce from the asset's existing
      quantity, and the amend inputs take no attribute values [Dev guide:
      `actions_obj_amend_assets`, `connect_requests_amend_input`]. On a bundle sized by a
      root attribute (locations, seats), "add 5 locations" is therefore not `quantityChange: 5`,
      which changes the root's own quantity and leaves the sizing attribute as it was.
    - **Changing the root's sizing answer on an amendment re-derives the children.** Amend
      the root with `quantityChange` 0, then set the answer with a Place request, rules on.
      Each CML-sized child came back as a delta line at its price. The root line took a
      cancel-and-reprice pair of detail rows at 0.00, so Help's cancel and reprice of an
      attribute amendment [Help: `ind.qocal_fdo_examples_of_amendment_types_and_results`]
      applied to the root line only. Activation wrote new state periods and
      "Change / Upsells" actions [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org].
      The cancel-and-reprice decision is made per line, from whether that line's own asset
      shows an attribute change, so a changed root can reprice while an unchanged child
      takes the plain delta path: expect mixed pricing shapes inside one bundle amendment.
      How a root answer change is mapped onto the child assets' attributes wasn't read
      [Platform behaviour, traced in part]. Quick Rule 2 has the reset of the other answers that comes with it.
    - An amendment that changes a component's plan or price is an amendment of the
      top-level asset too. Help describes a price amendment, which changes price without
      changing quantity, attributes or bundle configuration and works on bundles [Help:
      `ind.qocal_field_and_pricing_amendments`,
      `ind.qocal_field_and_price_amend_important_considerations`]. It does sit on a
      component's line: a new `UnitPrice` on the component line of a root amendment gave
      the quote action Amend / FieldAmendment, delta quantity 0, detail rows crediting each
      earlier lot at the old price and charging the full quantity at the new one, and, after
      activation, a new state period MRR and a "Change / Upsells" action [Measured:
      2026-11-11, 264, fresh `ent-sb0` scratch org]. A line that would have been No Change
      is promoted to Amend / FieldAmendment when a price or other mapped field differs from
      the latest state period's, checked only for assets with no attribute change; the
      priced result is a cancel-and-reprice pair with delta quantity 0 [Platform behaviour,
      traced in part]. How the change's date relative to existing or future state periods
      (a renewal's start, say) affects which period it is compared with wasn't isolated. A plan held as a root answer moved all
      of the component's units when the answer changed; moving part of them was refused in
      a model whose component group allows one plan
      ([change-policy-mapping.md](change-policy-mapping.md)). A plan held as an attribute
      on the component's line, and a swap of a component asset, are **Open**.
4. **Know where the price lands.**
    - On a renewal, a cancellation or a negative amendment, the unit price moves to
      `QuoteLineDetail` / `OrderItemDetail` rows, and the parent line's `UnitPrice` is null
      [Repo: `rlm-business-apis/SKILL.md`].
    - A pricing group keyed on net unit price admitted a reduction line, whose stored parent
      price is null, and its full-term value matched the expected value [Measured: 2026-11-12,
      264, scratch, one org]; that the net unit price is read from the pricing context is `[inferred]`. A per-lot renewal line
      has no net unit price at all: its prices sit on the per-lot detail rows, so such a group
      does not admit it ([../pricing-setup/scenarios/full-term-value.md](../pricing-setup/scenarios/full-term-value.md)).
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
      inside the policy's validity window [Platform behaviour, traced]. On the asset, a new
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
      state period for the renewal term. Standalone evergreen assets passed to a renewal
      request beside a Term Defined root came back as "No Change" lines at quantity 0, and
      their assets were untouched (no lifecycle end date, no new state period)
      [Measured: 2026-11-12, 264, scratch, one org]. To uplift them, send a price amendment (`quantityChange` 0, new `UnitPrice`)
      dated on the renewal start, after the renewal is activated; it was accepted on those
      standalone assets, with a new state period and a "Change / Upsells" action
      [Measured: 2026-11-12, 264, scratch, one org].
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
      year, 275/366 in a leap year). The day counts were measured only on contracts starting 1 January; that the partial period sits at the start and is calendar-aligned is `[inferred]` from them, and the period anchor for another start date is unmeasured; measure one mid-period change on a different start date before relying on it. A 30-day-month type counts 30 days a month. Not run: no such policy type was offered to create [Measured: 2026-11-12, 264, scratch, one org], so whether it reproduces a
      months-remaining source value on a mid-period start is unmeasured. A selling
      model's proration options take the policy only at create [read from the field describe, one org]. Turning
      partial periods off counts whole periods only. Read for the annual frequency with the
      actual-days type; that the first period runs to the calendar year end is inferred from
      the measured numbers, and other frequencies weren't read [Platform behaviour, traced
      in part]. A Term
      Defined top-level cancellation (`initiateCancellation`) and the invoice-level values
      are separate measurements ([verification.md](verification.md) → Open).
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
      `Asset.CurrentQuantity` still showed the old quantity after activation (unexplained); per-lot credits on a
      component weren't tested (one lot), and the Force path to an order wasn't completed. Evergreen swap credits are **Open** ([verification.md](verification.md) → Open).
    - A source's term-total value for an evergreen line (a total credit over the remaining
      term) doesn't compare with the quote directly: the quote counts the line for its
      pricing term count, not the term ([change-policy-mapping.md](change-policy-mapping.md)
      → Questions to settle in the plan).
7. **Constraints apply to amendments too.** A rule such as "a premium add-on only with the top plan"
   decides the order in which changes can run. Test each change sequence with
   configuration rules on. Help warns that an amendment of a future-dated order with
   CML products "doesn't conform to all the rules" [Help:
   `ind.qocal_future_dated_order_amendments_important_considerations`].
    - The measured rules did run on future-dated amendments: refusals and re-derivation
      matched a current-dated amendment's [Measured: 2026-11-11, 264, fresh `ent-sb0`
      scratch org]. Still assert each refusal's message rather than trusting a pass.
    - A rule can remove a line without a message. Changing a root answer so that an
      optional add-on's requirement (the add-on has a lower bound of 0) no longer held
      removed the add-on on the amendment silently, with `configure` success and no error
      log [Measured: 2026-11-11, 264]. Read the deltas of an answer change for lines the rep
      didn't touch.
    - **Why it is silent.** A line the caller doesn't fix is only a candidate for the solve,
      not a built component. That is the solver's general mechanism; in a context definition
      that tracks node status, a line with user status (kept from an earlier rep entry) is a
      real component; whether New or Changed lines count at that point wasn't shown. A requirement rule fires only
      when its condition holds, and a violated condition counts as satisfied, so the solver
      can satisfy the rule by choosing add-on count 0 and not instantiating the candidate:
      the line vanishes from the result, which becomes deltas, with success and no message.
      The rule's own message appears only when the count can't reach 0: the line is a real
      component (user status on the line, a user-set descendant or attribute, or a
      read-only/asset relation; a Changed line has a fixed quantity, but whether it is a real
      component wasn't shown), or the relation's minimum is above 0. Lines sourced from
      assets are fixed and conflict instead of dropping. To make a rule refuse rather than
      remove, give the relation a minimum above zero or tie the add-on to the answer the
      other way. Exclude rules refuse with their own message when the condition holds at
      satisfy time and a matching line exists; they remove matching lines silently when
      propagation decides the condition true before that (order-dependent). Removal
      considers matching lines of any origin, but a fixed line was seen to conflict instead,
      so whether a user-set line can be removed this way wasn't established. In the line-form copy the measured
      refusal named another rule's message: a failure on a constraint with no message of its
      own reports the first rule that failed or related rules' messages (inferred, not
      traced). Which status Place assigns an amendment add-on line wasn't read [Platform
      behaviour, traced in part].
    - Edit amendment lines through Place with `configurationMethod: Force`, as the earlier
      measured runs did (on a bundle quote, where Force flips other lines, `Skip` plus a
      `QuoteAction` Amend edit is the route that stayed scoped to one line, but it also let an incomplete bundle through to an order; see below). On a No Change amendment line (`quantityChange` 0), `Skip` with a non-zero
      quantity was refused (`isSuccess` false, INVALID_INPUT "Specify 0 in Quantity of the
      Quote Line Item record with the action of type No Change") and the line was unchanged;
      `Skip` with 0 succeeded and changed nothing. `Force` accepted the same edit and turned
      the line's `QuoteAction.Type` from No Change to Amend (`Quantity` the delta,
      `EndQuantity` = `StartQuantity` + delta). `Force` with quantity 0 also turned it to
      Amend, so a Force PATCH on a No Change line you meant to leave alone makes it an Amend
      line (what a Force-flipped line does at order and activation was not measured; a line flipped
      with Skip plus the `QuoteAction` Amend edit was ordered and activated, see Quick Rule 6). `Skip` with a `QuoteAction` PATCH setting `Type` Amend in the same request
      accepted the edit with the same end state [Measured: 2026-11-12, 264, scratch; one
      standalone Term Defined asset, System pricing, configuration rules at default; single-line
      amendment quotes, so whether Force also changes No Change lines not in the PATCH was not
      measured on those quotes (bundle runs below)]. On a three-line bundle amendment quote (root and two components, all No Change),
      `Skip` with quantity 1 on the Evergreen component was refused the same way, and `Force` with
      quantity 1 on the Term Annual component turned that line and both siblings (root included) to
      Amend, while `Force` on the Evergreen component (a separate quote, a -2 edit) turned only that line and the root, and its order was refused because the quote carried a bundle-validation Warning log (the test bundle lacked a required group's child, a test-setup gap; that the Force run wrote the log is inferred, since Force runs the configurator). `Skip` plus the
      `QuoteAction` Amend PATCH on the Term Annual component turned only that line [Measured:
      2026-11-12, 264, scratch, one org; why Force flipped siblings differently by component
      is unknown]. A Force edit can therefore change lines you didn't touch. On that same
      incomplete bundle, the `Skip` plus `QuoteAction` quote was ordered and activated while the
      `Force` quote was refused [Measured: 2026-11-12, 264, scratch, one org], so `Skip` let an
      incomplete bundle through to an order, and CML-sized children may not be re-derived
      [inferred].
      Use it for line-only edits and check rules and bundle validation separately. The message is a save-time quantity check that fires only while
      the action type is No Change and reads no configuration method; how `Force` changes the
      action type is not traced [Platform behaviour, traced in part]. On a new-business line
      `Force` and `Skip` both accepted non-zero edits and refused 0 (see constraint-models →
      quantities-from-attributes.md). Read every line's `QuoteAction.Type` back, not only the one you edited.
    - **A rule that counts a virtual container's lines needs those lines on the amendment.**
      Where the top-level lines were absent from a root-only amendment, the container's count
      rule fired (its message implied no matching lines) and logged an Error-severity entry,
      which blocks ordering (any configurator error-log row blocks ordering, Warning included;
      see change-policy-mapping.md; ordering wasn't attempted here). Amending the top-level assets at `quantityChange` 0 along with the
      root cleared it [Measured: 2026-11-12, 264, scratch org; one org]. The container counts
      only lines on the quote whose source matches the node it declares [Platform behaviour,
      traced]; that the added amendment lines bound to it is inferred from the cleared error,
      not read. Constraint side: `constraint-models`.
    - **The reverse, top-level lines without the root, raised no rule message.** An amendment of
      the top-level assets alone (one plan's line reduced, a new top-level line of the other
      plan added, no root) priced, ordered and activated with rules on, with 0 messages and no
      error log [Measured: 2026-11-12, 264, scratch, one org]. The container check that
      compares those lines with the root's answer didn't apply with no bundle on the quote, so
      those lines went unchecked [inferred, consistent with the no-bundle result in constraint-models]. A split rule that
      must hold on that path would need a quote-level validation that reads the assets (a
      custom build) [inferred].
    - **A root renewal carrying the held lines raised no rule message.** A renewal request for
      the root together with the container-held top-level evergreen support assets (they came
      back as "No Change" lines at quantity 0 with the assets untouched, Quick Rule 5) was
      ordered and activated with 0 messages and no error log [Measured: 2026-11-12, 264,
      scratch, one org]. A renewal of the root without the held lines wasn't run; by the
      root-only amendment result above, include them in the renewal request [inferred].
8. **Ramped bundles have their own limits:** amending an API-built group-ramped bundle
   with a one-time or evergreen child failed in the measured shapes
   [Repo: `ramped-quotes/bundle-children-lifecycle.md` → Amend and cancel limitation].
9. **Amending or cancelling assets whose order is still fulfilling may be limited by
   in-flight fulfillment.** A plain asset amendment was accepted with the Point of No Return
   flag copied to the step [Measured: 2026-11-13, 264, scratch, one org]; whether the state
   was in effect, and so enforcement, was not tested. A "no change after step X" rule needs
   its own validation `[inferred]`; see
   [dro-plans → updates-and-runtime.md](../dro-plans/updates-and-runtime.md) (PONR bullet).

## DO NOT

- **DO NOT** demo an inline quantity edit on an amendment of a configured product until
  the attribute reset is fixed. Change quantity with `initiateAmendment` and
  `quantityChange` (Quick Rule 2).
- **DO NOT** order an amendment that changed a CML answer before reading every line's delta:
  the answers it didn't change can reset to their defaults (Quick Rule 2).
- **DO NOT** promise a source's cancellation-credit or re-banding rule from the docs alone.
  Measure it on the selling models the model uses (Quick Rule 6, [verification.md](verification.md)).
- **DO NOT** trust `UnitPrice` or `NetUnitPrice` on renewal, cancellation or negative
  amendment lines, or on a positive amendment edited in the UI (Quick Rule 4).
- **DO NOT** roll back a backdated change; it is refused once the amendment period has
  started [Repo: `rlm-business-apis/backdated-asset-lifecycle.md`].

## Entry Conditions

| Situation | Use |
|---|---|
| Map a source's change policy (co-term, re-band, credits, renewal uplift) onto Revenue Cloud | This skill → [change-policy-mapping.md](change-policy-mapping.md) |
| Prove a change's numbers and attributes end to end | This skill → [verification.md](verification.md) |
| Backdated changes, invoices and credit memos | `rlm-business-apis` → `backdated-asset-lifecycle.md` |
| API request shapes (amend, renew, cancel, transfer, swap, upgrade, downgrade, rollback) | `rlm-business-apis`, `docs/api/transaction-management-apis-reference.md` |
| Build many renewal-ready assets or lifecycle history for a demo | `renewal-asset-creation` |
| Ramped (group ramp) quotes and their bundles | `ramped-quotes` → `bundle-children-lifecycle.md` |
| Renewal price uplift (price revision policy, CPI) | `pricing-setup` → `price-revision-policies.md`; `pricing-procedures` → `elements/price-revision-compound-uplift.md` |
| What the line editor shows on amendment, renewal and cancellation lines | `transaction-line-editor` |

## Sub-files

- [change-policy-mapping.md](change-policy-mapping.md): read when a source states rules for
  adds, swaps, cancellations and renewals, or gives a dated sequence of changes. Each rule
  maps to a platform action and what to check.
- [verification.md](verification.md): read when testing a change. It has the end-to-end
  test, the queries, the measured results, and what's still open.

## Examples

**"Add 5 locations mid-term, co-termed."** If the suite's quantity counts locations, amend the
top-level suite asset with `initiateAmendment`, using `quantityChange: 5` and
`amendStartDate` set to the mid-term date. If locations are a root attribute that sizes the children,
amend with `quantityChange` 0 and set the locations answer with a Place request, rules on; the
children re-derive as delta lines (Quick Rule 3). Then reprice, create the order and
activate. Check:
- the prorated value against the source's; Term Defined lines count the partial period by
  days, so months remaining ÷ 12 matches only on an anniversary (Quick Rule 6);
- the asset's new state period;
- that every other answer and attribute is unchanged (Quick Rule 2).

[change-policy-mapping.md](change-policy-mapping.md) has the volume-band question this
raises.

**"Cancel the support add-on but keep the device."** If the add-on is a bundle component,
cancelling it alone is refused, but an amendment of the bundle that sets the add-on's line
to −n removes it. That was measured on a Term Defined add-on, with a 0 state period and a
credit (Quick Rule 3); an evergreen add-on's removal to 0 is **Open**, and a one-lot partial
reduction is measured (Quick Rule 6). Decide in the plan
whether that is enough or the add-on must be its own line.

**"Move some units of a component to another plan."** If support is a bundle component, an
amendment has to act on the top-level asset (Quick Rule 3). A plan held as a root answer
moves all of the component's units, not some, and a split was refused where the component
group allows one plan. Whether a swap takes the component asset is undocumented.
[change-policy-mapping.md](change-policy-mapping.md) lists the paths with what to check;
pick one in the plan and measure it.

## Validation Checks

- For each change type the model promises, [verification.md](verification.md)'s test passes:
  price, quote total, order total, asset state period, asset action amount and category,
  and attributes.
- `python scripts/ai/analyze_agent_tooling.py check` passes after edits to this skill.
