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
2. **Read attributes as well as prices.** An inline quantity edit on an amendment line,
   with configuration rules on, resets the line's attributes to the product defaults.
   Activation keeps them on the asset, and the next amendment inherits them. The price
   stays right [Measured: 2026-11-05, 264]. Add quantity with `initiateAmendment` and
   `quantityChange`, which keeps them.
3. **Amend, renew and cancel act on top-level assets.** Cancelling or renewing a bundle
   component alone is refused: "the asset is a bundle component. Provide the top-level
   asset" [Measured: 2026-11-05, 264]. If a component must be cancellable on its own (a
   support plan, a warranty), sell it as its own line, not as a bundle component.
4. **Know where the price lands.**
    - On a renewal, a cancellation or a negative amendment, the unit price moves to
      `QuoteLineDetail` / `OrderItemDetail` rows, and the parent line's `UnitPrice` is null
      [Repo: `rlm-business-apis/SKILL.md`].
    - A positive API amendment keeps the price on the parent.
    - A positive amendment edited in the UI also moved its price to detail rows (+2 and −1
      at the unit price) [Measured: 2026-11-05, 264].
    - Read detail rows, or coalesce them, in anything that reports line prices.
5. **One-time and evergreen lines have no term to renew.** Renewing a one-time product
   with an evergreen component gave a $0 quote with quantity 0 on every line
   [Measured: 2026-11-05, 264]. Model a renewable commitment with a Term Defined selling
   model.
6. **Credits follow the selling model, not the effective date, on the quote.**
    - Cancelling a one-time product credited its full price at any date.
    - An evergreen annual or monthly component credited exactly one period at any date,
      from +1 to +400 days.
    - Both held on the Standard price book [Measured: 2026-11-05, 264]. Term Defined
      credits and the invoice-level values are separate measurements
      ([verification.md](verification.md) → Open).
7. **Constraints apply to amendments too.** A rule such as "Shield only with Premier"
   decides the order in which changes can run. Test each change sequence with
   configuration rules on.
8. **Ramped bundles have their own limits:** an API-built group-ramped bundle with a
   one-time or evergreen child can't be amended or cancelled
   [Repo: `ramped-quotes/bundle-children-lifecycle.md`].

## DO NOT

- **DO NOT** demo an inline quantity edit on an amendment of a configured product until
  the attribute reset is fixed. Use the API or the configurator.
- **DO NOT** promise a source's cancellation-credit or re-banding rule from the docs alone.
  Measure it on the selling models the model uses (Quick Rule 6, [verification.md](verification.md)).
- **DO NOT** trust `UnitPrice` or `NetUnitPrice` on renewal, cancellation or negative
  amendment lines (Quick Rule 4).
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
| What the Transaction Line Editor shows on these lines | `transaction-line-editor` |

## Sub-files

- [change-policy-mapping.md](change-policy-mapping.md): read when a source states rules for
  adds, swaps, cancellations and renewals. Each rule maps to a platform action and what to
  check.
- [verification.md](verification.md): read when testing a change. It has the end-to-end
  test, the queries, the measured results, and what's still open.

## Examples

**"Add 5 sites in month 7, co-termed."** Amend the top-level suite asset with
`initiateAmendment`, using `quantityChange: 5` and `amendStartDate` set to month 7. Then
reprice, create the order and activate. Check:
- the prorated value against the source's (months remaining ÷ 12 × annual for term lines);
- the asset's new state period;
- that the attributes are unchanged.

[change-policy-mapping.md](change-policy-mapping.md) has the volume-band question this
raises.

**"Cancel the support add-on but keep the device."** If the add-on is a bundle component,
cancelling it alone is refused (Quick Rule 3). Either the model changes (sell it as its
own line), or the demo cancels and re-adds the bundle. Decide this in the plan, not on
stage.

## Validation Checks

- For each change type the model promises, [verification.md](verification.md)'s test passes:
  price, quote total, order total, asset state period, asset action amount and category,
  and attributes.
- `python scripts/ai/analyze_agent_tooling.py check` passes after edits to this skill.
