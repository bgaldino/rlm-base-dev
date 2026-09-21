---
name: rlm-customer-demo-dro
description: >-
  Authors the customer-template-dro SFDMU dataset for Revenue Cloud customer demos —
  ProductFulfillmentDecompRule, ProductFulfillmentScenario, and Product2
  DecompositionScope updates over QB DRO infrastructure. Use when building or fixing
  customer demo DRO overlays, fulfillment step group mapping, null FulfillmentStepDefnGroupId,
  order decomposition, or an empty Fulfillment tab after order activation.
disable-model-invocation: true
---

# DRO builder

Owns `datasets/sfdmu/customer-template/en-US/customer-template-dro/**` and
`scripts/apex/deleteCustomerDemoDROData.apex`. Authoring only — never run `cci`, `sf`, or any
deploy/import command.

Input: `sku-contract.yaml` → `dro.scenarios`, and `org-context.json` for the real
`FulfillmentStepDefinitionGroup` names.

## What this overlay adds

1. `ProductFulfillmentDecompRule` — routes each sellable SKU to a QB operational sub-product
   (`QB-DRO-BILL` for Finance, `QB-DRO-PROJ` for Services)
2. `ProductFulfillmentScenario` — maps each SKU to a fulfillment step group per lifecycle
   action (Add, Amend, Renew, Cancel)
3. `Product2` Update — sets `DecompositionScope`: `Bundle` on bundle parents,
   `OrderLineItem` on everything else

It does **not** create step groups, step definitions, workspaces, or jeopardy rules. Those
come from `prepare_dro` and must already exist.

## The failure that wastes the most time

`FulfillmentStepDefinitionGroup.Name` values are **org-specific**. When SFDMU cannot resolve
the name it sets `FulfillmentStepDefnGroupId = null` with **no error** — the Fulfillment tab
just stays empty.

Use only the group names present in `org-context.json`. Never assume "Order Processing"; it
frequently does not exist. Typical mapping when those groups are present:

| Scenario purpose | Group |
|---|---|
| Finance / billing routing | `Finance` |
| Professional services delivery | `Services` |
| Subscription activation / provisioning | `Provisioning & Activation` |
| Platform-level provisioning | `Platform` |
| Usage metering activation | `Usage Provisioning & Activation` |

If a contract scenario names a group missing from `org-context.json`, stop and report it
rather than substituting a nearby name.

## Two object sets

Set 1 holds `Product2` and `FulfillmentStepDefinitionGroup` as `Readonly` (to build the FK
map across the whole org, including `QB-DRO-*` routing products) plus the PFDR and PFS
Upserts. Set 2 holds the `Product2` Update scoped to customer SKUs. This split avoids two
`Product2` entries in one object set.

Both PFDR and PFS use `operation: Upsert` with `externalId: Name`, so re-runs are safe.

`FulfillmentStepDefinitionGroup.csv` must exist even though the object is `Readonly` and
never written to the target. Without it the repo validator reports a Critical "declared
object has no CSV". A single `Name` column listing the org's step groups from
`org-context.json` satisfies it, and changes nothing at load time.

## Naming and scoping

Follow `<Prefix> <ProductName> to/- <Function>`. Scope
`scripts/apex/deleteCustomerDemoDROData.apex` to `customer.prefix`.

## Known non-issues

`ExecuteOnRuleId` and `ScenarioRuleId` are null on all PFDR and PFS records in most orgs.
That is normal and does not block DRO. `update_customer_demo_fulfillment_decomp_rules` is
retained as a Spring '26 safety measure, but missing fulfillment is almost always a null
`FulfillmentStepDefnGroupId` or a missing manual orchestration submit.

Decomposition does not always fire on order activation. "After you submit the orchestration
request…" on the Fulfillment tab is the expected post-activation state in manual-trigger
orgs — the user clicks **Submit Orchestration Request**.

## Before you finish

1. Every `step_group` value appears verbatim in `org-context.json`.
2. Every contract DRO SKU has PFDR rows and PFS rows for each listed action.
3. `DecompositionScope` is `Bundle` only on bundle parents.
4. Apex delete scope **adds** `customer.prefix` without dropping earlier customers'.
5. `FulfillmentStepDefinitionGroup.csv` exists.

If the contract routes a bundle parent's children unevenly, say so in your report rather than
inventing scenarios — selling a bundle whose children mostly lack scenarios decomposes only
the routed lines, which may or may not be the intended demo story.

Deeper detail: `datasets/sfdmu/customer-template/en-US/customer-template-dro/README.md`,
`docs/features/customer-demo-dro.md`.
