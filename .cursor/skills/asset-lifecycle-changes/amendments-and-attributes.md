# Asset Lifecycle Changes — Amendments, attributes, bundle components and constraints

> Sub-file of `.cursor/skills/asset-lifecycle-changes/SKILL.md`. Full detail for Quick Rules 2, 3 and 7: what an amendment does to attributes and CML answers, what acts on a bundle's top-level asset, and how rules behave on amendments.
> The numbered rules keep the numbers SKILL.md's Quick Rules cite.

## Rule 2: read attributes as well as prices

> The 2026-11-05 reset did not reproduce on a current build with node status present; blanking node status reproduces it [Measured: 2026-11-26, 264, ent-sb0 harness build], see [cancel-swap-and-linking.md](cancel-swap-and-linking.md#attribute-reset-on-amendment-not-reproduced). The configurator also restores a reset attribute (same section).

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
      [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org]. On another fresh build they
      held through three answer-change amendments, a line-only amendment and a renewal:
      after each activation every root asset action source row carried the node status,
      every answer at user status [Measured: 2026-11-17, 264, fresh `ent-sb0` scratch org].
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
## Rule 3: amend, renew and cancel act on top-level assets

3. **Amend, renew and cancel act on top-level assets.** Help's amend, renew and cancel
   procedures each say to select a bundle's parent asset, not the child [Help:
   `ind.qocal_amend_assets`, `ind.qocal_renew_assets`, `ind.qocal_cancel_assets`].
   Cancelling or renewing a bundle component alone is refused: "the asset is a bundle
   component. Provide the top-level asset" [Measured: 2026-11-05, 264].
    - **Usage-based renewals.** To carry negotiated rates and grants into the renewal quote,
      set the asset's Pricing Source to Last Transaction before renewing; blank or catalog
      pricing gives active catalog rates and grants [Help: `ind.qocal_renew_assets`]. Early
      renewal of usage-based assets needs a term-defined selling model (not one-time or
      evergreen) and the Revenue Cloud Advanced license without Billing
      [Help: `ind.qocal_renew_usage_based_assets_early`]. Neither was measured here.
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
      `actions-obj-amend-assets`, `connect-requests-amend-input`]. On a bundle sized by a
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
      2026-11-11, 264, fresh `ent-sb0` scratch org]. **Only configuration `Force` priced a
      price change on a component line.** `Skip` saved the new `UnitPrice` but left the line
      No Change at total 0. `Skip` with a `QuoteAction` PATCH to Amend turned the line Amend,
      still with no detail rows and total 0, under System and then Force pricing. `Force`
      wrote the credit and charge rows; it also turned a sibling component at quantity 0 to
      Amend, with one 0.00 detail row (Quick Rule 7) [Measured: 2026-11-17, 264, fresh
      `ent-sb0` scratch org; two Evergreen component lines]. A line that would have been No Change
      is promoted to Amend / FieldAmendment when a price or other mapped field differs from
      the latest state period's, checked only for assets with no attribute change; the
      priced result is a cancel-and-reprice pair with delta quantity 0 [Platform behaviour,
      traced in part]. How the change's date relative to existing or future state periods
      (a renewal's start, say) affects which period it is compared with wasn't isolated. A plan held as a root answer moved all
      of the component's units when the answer changed; moving part of them was refused in
      a model whose component group allows one plan
      ([change-policy-mapping.md](change-policy-mapping.md)). A plan held as an attribute
      on the component's line, and a swap of a component asset, are **Open**.

## Rule 7: constraints apply to amendments too

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
      line. A sibling at quantity 0 that a `Force` price edit flipped to Amend (one 0.00
      detail row) was ordered and activated with no error, and its state period stayed 0
      [Measured: 2026-11-17, 264, fresh `ent-sb0` scratch org]; a line flipped
      with Skip plus the `QuoteAction` Amend edit was ordered and activated, see Quick Rule 6. `Skip` with a `QuoteAction` PATCH setting `Type` Amend in the same request
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
      Use it for line-only quantity edits and check rules and bundle validation separately.
      It doesn't price a `UnitPrice` change on a component line; use `Force` for that (Quick
      Rule 3). `Force` edits on a complete bundle (a component's quantity, a root answer, a
      component's price) were each ordered and activated [Measured: 2026-11-17, 264, fresh
      `ent-sb0` scratch org]. The message is a save-time quantity check that fires only while
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
