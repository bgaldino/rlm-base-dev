# Usage Management Setup — Resources, Units, Policies, Grants

Read this when designing or reviewing the usage model of a product before any asset or
usage exists: enablement, permissions, units of measure, usage resources, policies,
grants, commitments, wallets. Parent skill: [SKILL.md](SKILL.md). Rates and rating
procedures: [`../rate-management/SKILL.md`](../rate-management/SKILL.md). Objects and fields:
[`usage.md`](../revenue-cloud-data-model/domains/usage.md). Drawdown behavior once sold:
[SKILL.md](SKILL.md) (How Drawdown Actually Works), not repeated here.

Labels: `[Help: id]` = `docs/salesforce/264/help/articles/ind.<id>.htm.md`;
`[inferred]` = reasoning only. Nothing here was measured by this file.

## Enablement and permissions

1. Setup, Usage Management Settings, enable Usage Management (Customize Application);
   enable Rate Management there too to get the rate objects
   [Help: `ind.um_enable_usage_management`].
2. Assign permission set licenses [Help: `ind.um_usage_management_psls_and_personas`]:

| License | Persona effect |
|---------|----------------|
| Usage Management Design Time | CRUD design-time objects, read runtime; designers, admin |
| Usage Management Run Time | CRUD runtime objects, read design time; adds account executives, customers |
| Wallet Management User | Read all; wallet viewers |

3. Guided workflow also needs Product Catalog Management Designer, Rate Management Design Time User
   and Usage Design User (or Usage Management Designer with Billing), plus Public Read/Write
   org-wide defaults on Unit of Measure, Unit of Measure Class, Usage Resource and the policy
   objects [Help: `ind.um_configure_usage_product_with_guided_workflow`].
4. Rate Management is enabled and permissioned separately; see
   [`../rate-management/SKILL.md`](../rate-management/SKILL.md) (Setup).

## Choose a setup path [Help: `ind.um_usage_management_setup`]

| Path | Choose when |
|------|-------------|
| Guided workflow (Products, Configure Usage Properties) | First-time anchor or pack product; wants cross-object validation and default policies |
| Manual records | Commitment products (quantity, monetary, token) or direct control of records |

Guided workflow limits [Help: `ind.um_guided_workflow_considerations`]: no commitment
products; edits only while records are Draft; up to 20 product usage resources per run
and 5 grants per resource; up to 3 required custom fields; a product usage resource takes
no custom fields. It reuses a policy with the same configuration instead of creating one,
and creates defaults named Aggregate Usage Monthly by Sum, Renew Grants Monthly, Rollover
Grants without Expiry, Overage Chargeable, Lowest Commitment Fulfilled Rate and Rate
Usage Monthly. Configuring rate records, price books or selling models changes, and
global rate cards shared by all products, are outside it.

## Manual sequence [Help: `ind.um_configure_usage_records`]

Each record depends on the earlier ones; follow the order.

| Step | Record | Decision to make |
|------|--------|------------------|
| 1 | Unit of measure class | Type Usage, Currency or Token; the class type must match the unit category [Help: `ind.um_create_unit_of_measure_class`] |
| 2 | Units of measure | Code, conversion factor to the class default, measurement type. A currency unit code must exactly match the org currency ISO code or rate cards silently disappear in selling [Help: `ind.um_create_units_of_measure`] |
| 3 | Usage-based product | Choose its usage model type on the product (anchor, pack, commitment) |
| 4 | Usage resource | Name and code, resource category Currency, Token or Usage, default unit, usage definition product [Help: `ind.um_create_usage_resource`] |
| 5 | Product usage resource | Link product to resource, effective dates, Optional (commitment products only), a token resource if charged in tokens; one token resource per product [Help: `ind.um_create_a_product_usage_resource`] |
| 6 | Product usage grant | Quantity, type Grant or Commit, drawdown order, validity, refresh and rollover policy [Help: `ind.um_define_a_product_usage_grant`] |
| 7 | Policies | Aggregation, rating frequency, overage, refresh, rollover |
| 8 | Grant binding policy | Self (default) or Target |
| 9 | Usage resource policy, then product usage resource policy | Bundle the policies; the product-level one overrides the resource-level one |
| 10 | Usage commitment policy | Rate after commitment is met |
| 11 | Commitment asset related object | Link a sold commitment to its anchor asset |

Records start Draft; Active records take limited edits [Help: `ind.um_create_usage_resource`].

## Policy decisions

| Policy | Options per Help | Source |
|--------|------------------|--------|
| Usage aggregation | Accumulation method Sum (all events) or Peak (maximum entry) over a period | [Help: `ind.um_create_usage_aggregation_policy`] |
| Rating frequency | Daily or Monthly; optional delay and delay unit | [Help: `ind.um_create_rating_frequency_policy`] |
| Overage | Whether overage is chargeable | [Help: `ind.um_create_usage_overage_policy`] |
| Grant refresh | Refresh allowed; frequency and unit (3 Month = quarterly) | [Help: `ind.um_create_usage_grant_refresh_policy`] |
| Grant rollover | Rollover allowed; optional expiry after a number of rollovers | [Help: `ind.um_create_usage_grant_rollover_policy`] |
| Commitment | Bounded Object Rate (overage at the bound asset rate) or Lowest Commitment Rate (overage at the committed rate) | [Help: `ind.um_create_usage_commitment_policy`] |
| Grant drawdown order | Expiring First (default), Granted First, Granted Last | [Help: `ind.um_define_a_product_usage_grant`] |

What to ask the customer: when does the allowance reset (refresh), does unused allowance
carry over (rollover), is overage billed, is the discount kept past the commitment
(commitment policy), should the bill count total or peak consumption (aggregation), how
often should rating run. Rule for commitment policy: Help says Bounded Object Rate suits
a discounted commitment with a separately defined overage rate; Lowest Commitment Rate
suits one unified rate [Help: `ind.um_create_usage_commitment_policy`].

Grant binding is the high-stakes choice: the binding target cannot change after the
order is activated and assetized, so a wrong target means redesigning the product
[Help: `ind.um_create_a_usage_product_grant_binding_policy`]. Self tracks each asset
alone; Target shares grants across accounts, contracts, products or a custom object.

Repo constraints for a commitment product's policy record are in
[SKILL.md](SKILL.md) (Quick Rules 6 and DO NOT list); they are repo findings, not Help.

## Grants, commitments and wallets

- Anchor, pack and commitment drawdown behavior, buckets, and token commitment
  conversion (usage to tokens, then tokens to currency):
  [Help: `ind.um_anchor_product_drawdowns`, `ind.um_pack_product_drawdowns`,
  `ind.um_commitment_product_drawdowns`, `ind.um_token_commitment_drawdowns`].
- Wallets: the Unified Usage Dashboard on account or asset pages shows balances,
  overages and rates; a customer wallet view needs Experience Cloud setup and navigation
  [Help: `ind.um_wallet_management`, `ind.um_set_up_menu_access`].
  Whether the dashboard works against this repo's seeded data is not measured.
- Billing for usage products handles late usage and extra orders
  [Help: `ind.um_billing_schedules_for_usage_products`]; see `billing-setup`.

## Limits that shape a design [Help: `ind.um_usage_management_limits`]

- A usage product cannot be a bundle parent or a bundle child; sell it as its own line.
- Usage Selling does not support: evergreen or one-time anchor products, start-date and end-date
  amendments, account and asset transfers, an amendment of a usage-based product that mixes a
  future-dated and a back-dated change, upgrades, downgrades and swaps, backdated amendments,
  backdated renewals and backdated cancellations, amendment rollbacks, revival of canceled assets,
  and pausing and resuming assets. Early renewals and renewals of expired assets are supported for
  Usage Selling but not for Consumption Management.
- Consumption Management does not process monetary or quantity commitment products and
  needs Usage Selling.

## Validate

Run the Usage Product Validator from the product record page (add the component and set
a usage model type first). It checks only effective, active records and warns when
consecutive product usage resources or consecutive rate card entries, or the product usage
resource and its first or last rate card entry, are more than 12 hours apart (the end check
only if the product usage resource has an end date)
[Help: `ind.um_run_validator`, `ind.um_considerations_for_validator`]. If you change the
usage model type after creating the related records, recheck them by hand first. Then
verify rating and consumption with [verification.md](verification.md).
