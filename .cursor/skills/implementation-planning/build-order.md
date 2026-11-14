# Build Order: Cross-Domain Prerequisites

Read this when sequencing build items for a customer plan, or when checking that a plan
does not build something before what it needs. The graph below is in neutral terms. Each
edge cites the source that states it; an edge tagged `[inferred]` follows from how the
objects reference each other and needs confirming in the target org before the plan
depends on it. Where a stage has no stated edge, build items in it are independent.

## Prerequisite graph

Read each row as "needs the rows above it, as listed". Items in one stage can run in
parallel unless an edge says otherwise.

| Stage | Build item | Needs | Edge source | Owner |
|---|---|---|---|---|
| 0 | Target, release, features, permissions | Nothing | [Setup order](../pricing-setup/SKILL.md#setup-order) (enablement first), [org-enablement-and-permissions.md](../pricing-setup/org-enablement-and-permissions.md) | [pricing-setup](../pricing-setup/SKILL.md) |
| 1 | Custom fields the later layers map | Stage 0 | [dependency-ordering.md](../repo-integration/dependency-ordering.md#pre-deploy-numbered-directories): a context mapping needs its field | [repo-integration](../repo-integration/SKILL.md) |
| 1 | Catalog: products, attributes, classifications, bundles, categories | Stage 0 | [product-catalog-modeling](../product-catalog-modeling/SKILL.md) | [product-catalog-modeling](../product-catalog-modeling/SKILL.md) |
| 2 | Selling models and options per product | Catalog | [Quick Rules](../product-catalog-modeling/SKILL.md#quick-rules) (option per model) | [selling-models-and-lifecycle.md](../product-catalog-modeling/selling-models-and-lifecycle.md) |
| 3 | Price books and entries; cost books if used | Products, selling models (entries carry the model) | [Setup order](../pricing-setup/SKILL.md#setup-order), [price-books.md](../pricing-setup/price-books.md) | [pricing-setup](../pricing-setup/SKILL.md) |
| 3 | Adjustment schedules, revision policies | Catalog, selling models, price books `[inferred]` | [Setup order](../pricing-setup/SKILL.md#setup-order) | [pricing-setup](../pricing-setup/SKILL.md) |
| 3 | Context definition, mappings, tags | Custom fields | [Setup order](../pricing-setup/SKILL.md#setup-order), [context-service](../context-service/SKILL.md) | [context-service](../context-service/SKILL.md) |
| 4 | Decision tables defined, data loaded, refreshed | Price books and source data they read | [Setup order](../pricing-setup/SKILL.md#setup-order), [The timing rule](../decision-tables/SKILL.md#the-timing-rule) | [decision-tables](../decision-tables/SKILL.md) |
| 4 | Recipe and table mappings | Decision tables, context | [pricing-wiring](../pricing-wiring/SKILL.md#reusable-layering-model) | [pricing-wiring](../pricing-wiring/SKILL.md) |
| 5 | Pricing procedure: elements, simulate, activate, set in revenue settings | Recipe, tables fresh, context tags | [Setup order](../pricing-setup/SKILL.md#setup-order), [Activation after a decision table change](../pricing-procedures/procedure-anatomy-and-ordering.md#activation-after-a-decision-table-change) | [pricing-procedures](../pricing-procedures/SKILL.md), [expression-sets](../expression-sets/SKILL.md) |
| 6 | Constraint models | Catalog bundles and their members | [constraint-models](../constraint-models/SKILL.md) `[inferred]` | [constraint-models](../constraint-models/SKILL.md) |
| 6 | Approvals: matrix, flows, pricing flags | Pricing procedure for any level it calculates; notification content | [advanced-approvals](../advanced-approvals/SKILL.md), [What the repo ships](../advanced-approvals/SKILL.md#what-the-repo-ships) | [advanced-approvals](../advanced-approvals/SKILL.md) |
| 6 | Billing policies, treatments, payment terms | Catalog (products they apply to) | [Billing policies and treatments](../billing-setup/SKILL.md#billing-policies-and-treatments) | [billing-setup](../billing-setup/SKILL.md) |
| 6 | Fulfillment configuration | Catalog products it decomposes; context and rule resources it reads | [dro-plans Quick Rules](../dro-plans/SKILL.md#quick-rules) (parents before children), [authoring-and-deployment.md](../dro-plans/authoring-and-deployment.md) | [dro-plans](../dro-plans/SKILL.md) |
| 6 | Contract setup | Feature access, settings, then types and states, then content | [salesforce-contracts Quick Rules](../salesforce-contracts/SKILL.md#quick-rules) | [salesforce-contracts](../salesforce-contracts/SKILL.md) |
| 6 | Usage resources, rating policies, commitments | Catalog, billing policies on usage resources, then rates | [dependency-ordering.md](../repo-integration/dependency-ordering.md#data-dependencies), [usage-consumption](../usage-consumption/SKILL.md) | [usage-consumption](../usage-consumption/SKILL.md) |
| 7 | Quote and order UI, line editor, documents | Procedure active, catalog, templates after their data mappers | [transaction-line-editor](../transaction-line-editor/SKILL.md), [document-generation](../document-generation/SKILL.md) | same |
| 8 | First transaction: quote, price, place | Stages 3 to 6 as the deal requires | [rlm-business-apis](../rlm-business-apis/SKILL.md#transaction-lifecycle-apis) | [rlm-business-apis](../rlm-business-apis/SKILL.md) |
| 9 | Order activation, fulfillment, billing schedules, assets | Placed order; fulfillment and billing configuration | [acceptance-chain.md](acceptance-chain.md) | [dro-plans](../dro-plans/SKILL.md), [billing-setup](../billing-setup/SKILL.md) |
| 10 | Lifecycle changes: amend, swap, cancel, renew | An asset exists | [asset-lifecycle-changes](../asset-lifecycle-changes/SKILL.md), [renewal-asset-creation](../renewal-asset-creation/SKILL.md) | same |
| 10 | Usage recording and rating | A usage-entitled asset | [The Pipeline](../usage-consumption/SKILL.md#the-pipeline) | [usage-consumption](../usage-consumption/SKILL.md) |

Edges the skills state only for one domain, and not as part of a cross-domain graph, are
listed above with their source. Edges the table marks `[inferred]` and any edge between
stages 6 and 9 that this table leaves implicit (for example what billing needs from
fulfillment) are not established by a skill: log them as open and verify live.

### Refresh and activation triggers

A change in one domain makes lookups in another stale. Plan a refresh after each:

| After changing | Refresh or reactivate | Source |
|---|---|---|
| Products, price book entries, rates, contracts feeding a table | The decision tables that read them | [decision-tables](../decision-tables/SKILL.md), [Freshness](../decision-tables/SKILL.md#freshness--what-the-verdicts-mean) |
| A decision table definition | The procedure that uses it, after the table | [Activation after a decision table change](../pricing-procedures/procedure-anatomy-and-ordering.md#activation-after-a-decision-table-change) |
| Newly loaded catalog content | The decision tables and the catalog search index, then wait for the index build; which of the two Place needed is not shown | [PCM load facts](../product-catalog-modeling/catalogs-and-loading.md#pcm-load-facts-264) (fact f) |
| Rating records | Activation in dependency order | [dependency-ordering.md](../repo-integration/dependency-ordering.md#post-load-activation-patterns) |

Refresh a table when its source criteria become true, not when the source row is written
([The timing rule](../decision-tables/SKILL.md#the-timing-rule)).

## Cross-check against this repo's flow

The repo realizes a subset of the graph as the `prepare_rlm_org` flow in `cumulusci.yml`,
documented in
[dependency-ordering.md](../repo-integration/dependency-ordering.md#prepare_rlm_org-step-ordering).
Use it to confirm an edge, never as the customer plan. Cited by sub-flow name, not number;
`tests/test_doc_build_steps.py` tracks numeric step citations, so none are used here.

| Graph stage | Realized by | Notes |
|---|---|---|
| 0, 1 (settings, fields, context definitions) | `prepare_core` | Settings, licenses, context definitions and pre-deploy metadata come first |
| 4 (tables) | `prepare_decision_tables`, then `refresh_all_decision_tables` late | Definitions early; the full refresh runs after all data is loaded |
| 5 (procedures) | `prepare_expression_sets`, then `activate_and_deploy_expression_sets` | Deploy early; activation after data and rating |
| 1, 2 (catalog) | `prepare_product_data` | After `deploy_full` and the schedule metadata |
| 3 (prices) | `prepare_price_adjustment_schedules`, `prepare_pricing_data` | Pricing data loads after the catalog |
| 5 (revenue settings) | `prepare_revenue_settings` | Runs late, after constraints and guided selling |
| 6 (fulfillment) | `prepare_dro` | After pricing data |
| 6 (billing, usage) | `prepare_billing`, `prepare_rating` | Rating follows billing, as the data dependencies require |
| 6 (contracts) | `prepare_clm` | |
| 6 (approvals) | `prepare_approvals_pricing` | After expression-set activation |
| 6 (constraints) | `prepare_constraints` | After the catalog |
| 7 (documents) | `prepare_docgen` | Runs early, right after pricing data and before fulfillment |
| 7 (UX) | `prepare_ux` | Runs late, after objects and pages exist |
| 9 (readiness) | `prepare_pricing_discovery`, `rebuild_search_index` | End-of-build refreshes |

The flow is ordered for one scripted build, so it also contains repo-specific items (demo
catalog, personas, in-app learning, agents, community) that no customer graph needs unless
asked. Where the flow and the graph disagree, the flow reflects a repo constraint (for
example shared sample data). Order differs too: documents are built early in the flow but sit at
stage 7 in the graph, and revenue settings are set late in the flow but sit at stage 5;
decide per plan and record why.

To re-verify the cross-check when the flow changes, list its steps (`cci flow info
prepare_rlm_org`) or read the flow in `cumulusci.yml`, and compare names. This file cites
no step numbers, so `tests/test_doc_build_steps.py` has nothing here to track.

## Parallelism and gates

- Stages 3 and 6 contain independent items; assign them to separate workers only when each
  owner's prerequisites are met.
- A stage's exit check is the owner's org-verification checks where it has them (an owner
  with none is an open item, logged), not the stage's completion in
  tooling. Do not start a stage that depends on a table or procedure until the freshness
  and activation checks pass.
- Record each edge you rely on that is `[inferred]` or open in the decision log.
