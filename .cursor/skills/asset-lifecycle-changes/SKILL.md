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

Use this skill when a model has to survive after the sale: a customer adds sites,
moves to a cheaper plan, cancels an add-on or renews at a new price. The domain
skills cover the individual APIs. This one covers the modeling decisions and the
behaviour you have to verify, because Help describes how to set lifecycle changes up but
not the numbers they produce. Claims are tagged `[Help: <article>]`, `[Dev guide: <article>]`,
`[Repo: <path>]` and `[Measured: <date>, 264]`. The 2026-11-05 runs were on QuantumBit
builds. The 2026-11-11 runs were on fresh 264 `ent-sb0` scratch orgs, on a bundle sized by
CML root answers, priced by a procedure cloned from the shipped default with overlays,
with configuration rules on ([verification.md](verification.md) → Measured
results, 2026-11-11).

## Quick Rules

1. **Decide each change type's numbers before you build, then test them past the first
   placement.** Follow the change from quote → reprice → order → reprice → activation →
   asset state periods → asset actions. A value that is right on the quote can still
   drift later ([verification.md](verification.md)).
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
      no answer in the request, kept every answer. On one of those orgs (the reset reproduced
      on a second) `AssetActionSource.RLM_ConstraintEngineNodeStatus__c` was empty after
      every activation while the order lines carried it, so amendment lines started with no node status
      [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org].
    - Two workarounds held. Restate, in a second Place request, every answer that reset to
      its default (it now differs, so it counts as a change). Or, before amending, copy each
      order line's node status onto the asset action sources that reference it. Why the
      asset action sources lack it is **Open**. Read every line's delta before ordering.
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
      a Term Defined component was removed; an evergreen component's credit on removal is
      **Open** (Quick Rule 6). A component that must be cancelled on its own, into a terminal state, still has to be
      sold as its own line.
    - `quantityChange` is the quantity to add to or reduce from the asset's existing
      quantity, and the amend inputs take no attribute values [Dev guide:
      `actions_obj_amend_assets`, `connect_requests_amend_input`]. On a bundle sized by a
      root attribute (sites, users), "add 5 sites" is therefore not `quantityChange: 5`,
      which changes the root's own quantity and leaves the sizing attribute as it was.
    - **Changing the root's sizing answer on an amendment re-derives the children.** Amend
      the root with `quantityChange` 0, then set the answer with a Place request, rules on.
      Each CML-sized child came back as a delta line at its price. The root line took a
      cancel-and-reprice pair of detail rows at 0.00, so Help's cancel and reprice of an
      attribute amendment [Help: `ind.qocal_fdo_examples_of_amendment_types_and_results`]
      applied to the root line only. Activation wrote new state periods and
      "Change / Upsells" actions [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org].
      Quick Rule 2 has the reset of the other answers that comes with it.
    - An amendment that changes a component's plan or price is an amendment of the
      top-level asset too. Help describes a price amendment, which changes price without
      changing quantity, attributes or bundle configuration and works on bundles [Help:
      `ind.qocal_field_and_pricing_amendments`,
      `ind.qocal_field_and_price_amend_important_considerations`]. It does sit on a
      component's line: a new `UnitPrice` on the component line of a root amendment gave
      the quote action Amend / FieldAmendment, delta quantity 0, detail rows crediting each
      earlier lot at the old price and charging the full quantity at the new one, and, after
      activation, a new state period MRR and a "Change / Upsells" action [Measured:
      2026-11-11, 264, fresh `ent-sb0` scratch org]. A plan held as a root answer moved all
      of the component's units when the answer changed; moving part of them was refused in
      a model whose component group allows one plan
      ([change-policy-mapping.md](change-policy-mapping.md)). A plan held as an attribute
      on the component's line, and a swap of a component asset, are **Open**.
4. **Know where the price lands.**
    - On a renewal, a cancellation or a negative amendment, the unit price moves to
      `QuoteLineDetail` / `OrderItemDetail` rows, and the parent line's `UnitPrice` is null
      [Repo: `rlm-business-apis/SKILL.md`].
    - A positive API amendment keeps the price on the parent.
    - A positive amendment edited in the UI also moved its price to detail rows (+2 and −1
      at the unit price) [Measured: 2026-11-05, 264].
    - A reduction's detail rows came one per earlier lot it drew from, last in, first out.
      A renewal priced each lot on its own row [Measured: 2026-11-11, 264, fresh `ent-sb0`
      scratch org].
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
      state period for the renewal term. A standalone evergreen asset's renewal wasn't
      measured.
6. **On the quote, credits follow the selling model.** For one-time and evergreen lines
   the effective date didn't matter. At every date tested (+1, +30, +180, +300 and +400
   days):
    - cancelling a one-time product credited its full price;
    - an evergreen annual or monthly component credited exactly one period.
    - Both held on the Standard price book [Measured: 2026-11-05, 264].
    - A Term Defined component reduced to 0 through a root amendment credited quantity ×
      net unit price × the remaining term count. The Default Proration Policy that `qb-pcm`
      ships [Repo: `datasets/sfdmu/qb/en-US/qb-pcm/ProrationPolicy.csv`] counted whole annual periods left plus the days left in the current one ÷ that
      period's days (184/366 in a leap year), so a months-remaining figure matches only on
      an anniversary [Measured: 2026-11-11, 264, fresh `ent-sb0` scratch org]. A Term
      Defined top-level cancellation (`initiateCancellation`) and the invoice-level values
      are separate measurements ([verification.md](verification.md) → Open).
    - The only quantity credit measured on an evergreen line is the cancellation's above (a
      price amendment's credit rows are in Quick Rule 3). Help says
      an evergreen reduction takes units last in, first out from the current quantity, and
      a swap acts as an add plus a negative amendment [Help:
      `ind.qocal_fdo_examples_of_amendment_types_and_results`], but not what either credits.
      Evergreen reduction and swap credits are **Open** ([verification.md](verification.md)
      → Open).
    - A source's term-total value for an evergreen line (a total credit over the remaining
      term) doesn't compare with the quote directly: the quote counts the line for its
      pricing term count, not the term ([change-policy-mapping.md](change-policy-mapping.md)
      → Questions to settle in the plan).
7. **Constraints apply to amendments too.** A rule such as "Shield only with Premier"
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
    - Editing an amendment line through Place needs `configurationMethod: Force`; with
      `Skip` it was refused ("Specify 0 in Quantity of the Quote Line Item record with the
      action of type No Change") [Measured: 2026-11-11, 264].
8. **Ramped bundles have their own limits:** amending an API-built group-ramped bundle
   with a one-time or evergreen child failed in the measured shapes
   [Repo: `ramped-quotes/bundle-children-lifecycle.md` → Amend and cancel limitation].

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

**"Add 5 sites in month 7, co-termed."** If the suite's quantity counts sites, amend the
top-level suite asset with `initiateAmendment`, using `quantityChange: 5` and
`amendStartDate` set to month 7. If sites are a root attribute that sizes the children,
amend with `quantityChange` 0 and set the sites answer with a Place request, rules on; the
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
credit (Quick Rule 3); an evergreen add-on's credit is **Open**. Decide in the plan
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
