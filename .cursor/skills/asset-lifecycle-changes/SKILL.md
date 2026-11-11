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
`[Repo: <path>]` and `[Measured: <date>, 264]`. The measured runs were on QuantumBit builds
in November 2026.

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
3. **Amend, renew and cancel act on top-level assets.** Help's amend, renew and cancel
   procedures each say to select a bundle's parent asset, not the child [Help:
   `ind.qocal_amend_assets`, `ind.qocal_renew_assets`, `ind.qocal_cancel_assets`].
   Cancelling or renewing a bundle component alone is refused: "the asset is a bundle
   component. Provide the top-level asset" [Measured: 2026-11-05, 264]. If a component must
   be cancellable on its own (a support plan, a warranty), sell it as its own line, not as a
   bundle component.
    - `quantityChange` is the quantity to add to or reduce from the asset's existing
      quantity, and the amend inputs take no attribute values [Dev guide:
      `actions_obj_amend_assets`, `connect_requests_amend_input`]. On a bundle sized by a
      root attribute (sites, users), "add 5 sites" is therefore not `quantityChange: 5`,
      which changes the root's own quantity and leaves the sizing attribute as it was.
    - Help's future-dated examples describe an attribute amendment as a new value set on
      the line, processed as a cancel and reprice [Help:
      `ind.qocal_fdo_examples_of_amendment_types_and_results`]. Whether changing the root's
      sizing attribute on an amendment re-derives the children through CML is **Open**
      ([verification.md](verification.md) → Open).
    - An amendment that changes a component's plan or price is an amendment of the
      top-level asset too. Help has two amendments that keep the bundle: the attribute
      amendment above, and a price amendment, which changes price without changing
      quantity, attributes or bundle configuration and works on bundles [Help:
      `ind.qocal_field_and_pricing_amendments`,
      `ind.qocal_field_and_price_amend_important_considerations`]. Neither says whether the
      change can sit on a component's line. A swap is a separate route, and no snapshot
      article says whether it takes a component asset. All three are **Open**
      ([change-policy-mapping.md](change-policy-mapping.md)).
4. **Know where the price lands.**
    - On a renewal, a cancellation or a negative amendment, the unit price moves to
      `QuoteLineDetail` / `OrderItemDetail` rows, and the parent line's `UnitPrice` is null
      [Repo: `rlm-business-apis/SKILL.md`].
    - A positive API amendment keeps the price on the parent.
    - A positive amendment edited in the UI also moved its price to detail rows (+2 and −1
      at the unit price) [Measured: 2026-11-05, 264].
    - Read detail rows, or coalesce them, in anything that reports line prices.
5. **One-time lines have no term to renew.** Renewing a one-time product sets its
   quantity to zero [Help: `ind.qocal_asset_lifecycle_considerations`]. Renewing a one-time
   product with an evergreen component gave a $0 quote with quantity 0 on every line
   [Measured: 2026-11-05, 264]; a standalone evergreen renewal wasn't measured. Model a
   renewable commitment with a Term Defined selling model.
6. **Credits follow the selling model, not the effective date, on the quote.** At every
   date tested (+1, +30, +180, +300 and +400 days):
    - cancelling a one-time product credited its full price;
    - an evergreen annual or monthly component credited exactly one period.
    - Both held on the Standard price book [Measured: 2026-11-05, 264]. Term Defined
      credits and the invoice-level values are separate measurements
      ([verification.md](verification.md) → Open).
    - The only credit measured on an evergreen line is the cancellation's above. Help says
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
   `ind.qocal_future_dated_order_amendments_important_considerations`], so a passing
   future-dated amendment doesn't prove the rules held.
8. **Ramped bundles have their own limits:** amending an API-built group-ramped bundle
   with a one-time or evergreen child failed in the measured shapes
   [Repo: `ramped-quotes/bundle-children-lifecycle.md` → Amend and cancel limitation].

## DO NOT

- **DO NOT** demo an inline quantity edit on an amendment of a configured product until
  the attribute reset is fixed. Change quantity with `initiateAmendment` and
  `quantityChange` (Quick Rule 2).
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
`amendStartDate` set to month 7. If sites are a root attribute that sizes the children, a
quantity change doesn't move it (Quick Rule 3); settle that path in the plan first. Then
reprice, create the order and activate. Check:
- the prorated value against the source's (months remaining ÷ 12 × annual for term lines);
- the asset's new state period;
- that the attributes are unchanged.

[change-policy-mapping.md](change-policy-mapping.md) has the volume-band question this
raises.

**"Cancel the support add-on but keep the device."** If the add-on is a bundle component,
cancelling it alone is refused (Quick Rule 3), and removing it through an amendment of the
bundle is unmeasured. Either sell it as its own line, or measure the amendment path first.
Decide this in the plan, not on stage.

**"Move 10 sites from Premier to Standard support."** If support is a bundle component, an
amendment has to act on the top-level asset (Quick Rule 3), and whether a swap takes the
component asset is undocumented. None of the paths (an attribute amendment, separate
component products, a swap of the component) is measured on a component.
[change-policy-mapping.md](change-policy-mapping.md) lists them with what to check; pick one
in the plan and measure it.

## Validation Checks

- For each change type the model promises, [verification.md](verification.md)'s test passes:
  price, quote total, order total, asset state period, asset action amount and category,
  and attributes.
- `python scripts/ai/analyze_agent_tooling.py check` passes after edits to this skill.
