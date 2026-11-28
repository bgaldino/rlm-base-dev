# Contract pricing on bundles: what a contract price does to a root and its children

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`. Release 264 / API v68.0. The full contract-pricing
> guide (what a contract can carry, setup checklist, amendments, known limits) is
> [`docs/guides/contract-pricing.md`](../../../docs/guides/contract-pricing.md); the refresh that makes a new
> contract price visible to pricing is
> [`../decision-tables/lifecycle-and-refresh.md`](../decision-tables/lifecycle-and-refresh.md) (*Runtime-created pricing rows*).

Rows below were measured on a quote with a bundle root (list 300) and components. All rows:
[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build, one org].

| Case | Result |
|---|---|
| A Sales Price sent on the line equal to list price at create (Place API, before pricing set List Price), with a contract price present | The contract price is suppressed. Omit Sales Price and let pricing fill it |
| A contract price on the **root** line | The root line goes from 300 to 200 |
| A contract price on a **child** line, default component relationship | The child nets to 0 and does not change the total |
| A contract price on a child marked not included in the bundle price | The child's contract price shows in the total |

- A Bundle Based Adjustment acts on components only, never on the root, and gives a shared child a
  different net price under each parent, with or without a contract. Element side:
  [`../pricing-procedures/elements/bundle-based-price.md`](../pricing-procedures/elements/bundle-based-price.md).
- Activation refreshes the three `Contract_Pricing_*` tables (asynchronous); confirm the sync landed
  before pricing.
  [Repo: force-app/main/default/flows/RLM_Contract_Activation_Refresh_Pricing_Tables.flow-meta.xml]
- Refresh by hand after a bulk load, after rows are added to an activated contract, or after a
  draft-contract edit. [Repo: docs/guides/contract-pricing.md]
- Amend and price book behavior on asset changes (the amend action's date format, the fixed quote price
  book, entry price changes on amendment lines) belongs to the asset-lifecycle-changes skill.
