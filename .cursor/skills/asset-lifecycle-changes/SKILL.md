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
results, 2026-11-11). The 2026-11-17 runs replayed a dated sequence of amendments and a
renewal on one bundle contract, on a fresh 264 `ent-sb0` scratch org with the repo's
node-status rule and trigger ([verification.md](verification.md) → Measured results,
2026-11-17).

## Quick Rules

1. **Decide each change type's numbers before you build, then test them past the first
   placement.** Follow the change from quote → reprice → order → reprice → activation →
   asset state periods → asset actions. A value that is right on the quote can still drift later
   ([verification.md](verification.md)).
    - **Never reprice a renewal or cancellation (and, until measured, other amendment shapes and ramped quotes) quote after its order is activated.** Pricing of a renewal, amendment
      or cancellation line reads the source asset's current state and activation changes it [Platform behaviour,
      traced in part]. A full reprice (`Force`, configuration `Skip`) after activation set a renewal's lines and total
      to 0 [Measured: 2026-11-12, 264, scratch, one org] and an activated cancellation's line and total to 0
      [Measured: 2026-11-26, 264, ent-sb0 harness build; [cancel-swap-and-linking.md](cancel-swap-and-linking.md)]; an
      amend-add and an Evergreen-reduce amendment quote did not change [Measured: 2026-11-26, 264, ent-sb0 harness
      build]. Other amendment shapes, and any ramped quote, are not measured: keep the caution there. Why the reprice
      returned 0 is not traced. Read quote values before activation. A renewal quote that wasn't repriced still read its total after its order
      activated [Measured: 2026-11-17, 264, fresh `ent-sb0` scratch org].
2. **Read attributes as well as prices.** A quantity change on an amendment line placed with rules on can reset the
   line's attributes and, when a root answer changes, every answer the request didn't change goes back to its CML
   default. The cause appears to be a **missing configurator node status** on the source asset's action-source rows
   [Open: inferred from a blank-and-repeat test, not core-traced]; the repo's context rule and trigger fill it, and with both, answers held through repeated amendments and a renewal
   [Measured: 2026-11-11 and 2026-11-17, 264, fresh `ent-sb0` scratch orgs]. The 2026-11-05 reset did **not**
   reproduce on a current build with node status present [Measured: 2026-11-26, 264, ent-sb0 harness build]. After every
   activation in a multi-step replay, read the root's latest asset action source rows. Add quantity with
   `initiateAmendment` and `quantityChange`. Detail: [amendments-and-attributes.md](amendments-and-attributes.md#rule-2-read-attributes-as-well-as-prices).
3. **Amend, renew and cancel act on top-level assets.** Help says to select a bundle's parent asset
   [Help: `ind.qocal_amend_assets`, `ind.qocal_renew_assets`, `ind.qocal_cancel_assets`]; cancelling or renewing a
   component alone, and swapping a component asset, are refused [Measured: 2026-11-05 and 2026-11-26, 264]. To remove a
   Term Defined component, amend the root with `quantityChange` 0 and set the component line to -n (Place, rules on).
   `quantityChange` adds to the asset's own quantity, so "add 5 locations" on a root-attribute-sized bundle is a
   Place answer change that re-derives the children. A component price change prices only with configuration `Force`.
   Detail: [amendments-and-attributes.md](amendments-and-attributes.md#rule-3-amend-renew-and-cancel-act-on-top-level-assets).
4. **Know where the price lands.** On a renewal, cancellation or negative amendment the unit price moves to
   `QuoteLineDetail` / `OrderItemDetail` rows and the parent `UnitPrice` is null; a positive API amendment keeps it on
   the parent, a positive UI amendment moves it. A reduction draws from earlier lots last in, first out; a renewal
   prices each lot on its own row. Read detail rows (or `GrandTotal`), not a line-level roll-up. Detail:
   [prices-renewals-credits.md](prices-renewals-credits.md).
5. **One-time lines have no term to renew; Term Defined bundles renew in place** (same assets extended, "Change /
   Renewals"); evergreen components come back as No Change at quantity 0, and uplift them with a price amendment dated
   on the renewal start. Detail: [prices-renewals-credits.md](prices-renewals-credits.md#rule-5-one-time-lines-have-no-term-to-renew-term-defined-bundles-renew-in-place).
6. **On the quote, credits follow the selling model.** One-time: the full price. Evergreen: one period on the quote,
   but the **invoice** credits by day (a 2,000 per month line reduced by one unit: -1,000 invoiced against a -2,000 quote credit). Term Defined: quantity x net unit price
   x remaining periods **counted from the asset start** (a Term Defined cancel measured -10,510.03, not the
   calendar-year -10,518.95). State the quote and invoice values separately
   [Measured: 2026-11-26, 264; [cancel-swap-and-linking.md](cancel-swap-and-linking.md)].
7. **Constraints apply to amendments too.** Test each change sequence with rules on and assert each refusal's
   message. A rule can remove a line silently (a requirement the solver satisfies with count 0), a swap can add a
   required line dated today, and a Force edit can flip untouched lines to Amend: read every line's delta, date and
   `QuoteAction.Type`. Detail: [amendments-and-attributes.md](amendments-and-attributes.md#rule-7-constraints-apply-to-amendments-too).
8. **Ramped bundles have their own limits:** amending an API-built group-ramped bundle with a one-time or evergreen
   child failed in the measured shapes [Repo: `ramped-quotes/bundle-children-lifecycle.md` → Amend and cancel limitation].
9. **Amending or cancelling assets whose order is still fulfilling may be limited by in-flight fulfillment.** A plain
   amendment was accepted with the Point of No Return flag copied to the step [Measured: 2026-11-13, 264, scratch,
   one org]; whether the state was in effect, and so enforcement, was not tested. A "no change after step X" rule needs its own validation `[inferred]`; see
   [dro-plans → updates-and-runtime.md](../dro-plans/updates-and-runtime.md).

## DO NOT

- **DO NOT** demo an inline quantity edit on an amendment of a configured product without first checking the build:
  the 2026-11-05 runs reset the attributes [Measured: 2026-11-05, 264, QuantumBit build], and a current build with node
  status present kept them [Measured: 2026-11-26, 264, ent-sb0 harness build]. Change quantity with `initiateAmendment`
  and `quantityChange` (Quick Rule 2).
- **DO NOT** order an amendment that changed a CML answer before reading every line's delta:
  the answers it didn't change can reset to their defaults (Quick Rule 2).
- **DO NOT** promise a source's cancellation-credit or re-banding rule from the docs alone.
  Measure it on the selling models the model uses (Quick Rule 6, [verification.md](verification.md)).
- **DO NOT** trust `UnitPrice` or `NetUnitPrice` on renewal, cancellation or negative
  amendment lines, or on a positive amendment edited in the UI (Quick Rule 4).
- **DO NOT** roll back a backdated change; it is refused once the amendment period has
  started [Repo: `rlm-business-apis/backdated-asset-lifecycle.md`].
- **DO NOT** reprice a renewal or cancellation (and, until measured, other amendment shapes and ramped quotes) after its order is activated (Quick Rule 1).
- **DO NOT** quote an evergreen credit from the quote alone: the invoice credits by day (Quick Rule 6).
- **DO NOT** state a Term Defined cancel credit from calendar years: it counts from the asset start (Quick Rule 6).

## Entry Conditions

| Situation | Use |
|---|---|
| Map a source's change policy (co-term, re-band, credits, renewal uplift) onto Revenue Cloud | This skill → [change-policy-mapping.md](change-policy-mapping.md) |
| Prove a change's numbers and attributes end to end | This skill → [verification.md](verification.md) |
| Cancellation, evergreen credit, swap, linking a renewal to an Opportunity or open quote | This skill → [cancel-swap-and-linking.md](cancel-swap-and-linking.md) |
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
- [amendments-and-attributes.md](amendments-and-attributes.md): read before an amendment of a configured bundle: attribute and answer resets, bundle components, Force and Skip, constraint behaviour (Quick Rules 2, 3, 7).
- [prices-renewals-credits.md](prices-renewals-credits.md): read when reading or promising prices on renewal, cancellation or reduction lines, or credits by selling model (Quick Rules 4, 5, 6).
- [cancel-swap-and-linking.md](cancel-swap-and-linking.md): read for Term Defined cancellation, evergreen quote vs invoice credit, swaps and their refusals, and linking renewals and amendments to Opportunities, open quotes and contracts.

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
group allows one plan. A swap of the component asset is refused ("the asset is a bundle child") [Measured: 2026-11-26, 264, ent-sb0 harness build]; swap the top-level asset.
[change-policy-mapping.md](change-policy-mapping.md) lists the paths with what to check;
pick one in the plan and measure it.

**"Renew at each lot's current price plus N%, and raise support by N% too."** Put the price
revision policy and `UnitPriceUplift` on the new-sale Term Defined lines; lots added by
amendment inherit them. Renew the root with an end date, so each lot renews at its own price
plus the uplift (Quick Rule 4). Evergreen support isn't uplifted by the renewal: after it
activates, amend the root dated on the renewal start and set the support lines' new
`UnitPrice` with configuration `Force` (Quick Rules 3 and 5). Report the renewal total from
`GrandTotal`, and a combined total by adding the support change yourself: no single record
holds both.

## Validation Checks

- For each change type the model promises, [verification.md](verification.md)'s test passes:
  price, quote total, order total, asset state period, asset action amount and category,
  and attributes.
- `python scripts/ai/analyze_agent_tooling.py check` passes after edits to this skill.

