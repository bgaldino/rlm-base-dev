# Build Order: Cross-Domain Prerequisites

Read this when sequencing build items for a customer plan, or when checking that a plan
does not build something before what it needs. The graph below is in neutral terms. Each
edge cites the source that states it; an edge tagged `[inferred]` is not stated by a source
(it follows from how the objects reference each other, the repo flow's order, or the
absence of a recorded edge) and needs confirming in the target org before the plan
depends on it. Where no skill records an edge between items in a stage, treat them as
independent `[inferred]` and log that as open.

The plan's phases ([plan-template.md](plan-template.md) section 5) group these stages: P0
is stage 0, P3 stages 1 and 2 plus the constraint models (P3 builds the context
definition and tags they read first, or waits for P4's), P4 stages 3 to 5, P5 the
approvals and stage 7, and P6 the rest of stage 6 and stages 9 and 10. P2 spikes build
only the stages their must-hits need, on their own org. A test that places a quote before P4
(a P2a spike, or P3's configuration test: a bundle test places the quote with rules on, PCM
fact e) first needs price book entries for its products and the refresh newly loaded
products need (fact f) `[inferred]`; the priced transaction (stage 8) is first gated at P4. A P2b chain whose fulfilment its must-hits count loads its
fulfilment configuration before its first order (a submitted plan doesn't pick up later configuration,
`dro-plans`); load the other stage 6 configuration its orders read first too `[inferred]`. Where the source shows tax or usage
rates on the quote, or its quote lines bill on a cadence other than the pricing term or by
milestone, build those stage 6 items in P4 with their own prerequisites (tax engine,
policies and legal entity; usage resources, rate cards and their refreshed rating tables;
billing policy and treatments), or leave them out of the P4 goldens
and record the decision. Where a plan puts an item in a different phase, record why in
the decision log.

## Prerequisite graph

Each row's Needs cell lists the main prerequisites the cited sources state; read the owner
skill for the rest. The stage number groups items and is not a strict order (constraint models need the catalog and the context they read, not prices).
Items in one stage can run in parallel unless an edge says otherwise `[inferred]`.

| Stage | Build item | Needs | Edge source | Owner |
|---|---|---|---|---|
| 0 | Target, release, features, permissions, for pricing and each in-scope domain (billing, usage, contracts) | Nothing | [Setup order](../pricing-setup/SKILL.md#setup-order) (enablement first), [org-enablement-and-permissions.md](../pricing-setup/org-enablement-and-permissions.md) | [pricing-setup](../pricing-setup/SKILL.md), plus each domain's enablement section (for example [usage-setup.md](../usage-consumption/usage-setup.md#enablement-and-permissions)) |
| 1 | Custom fields the later layers map | Stage 0 | [dependency-ordering.md](../repo-integration/dependency-ordering.md#pre-deploy-numbered-directories): a context mapping needs its field | [repo-integration](../repo-integration/SKILL.md) |
| 1 | Unit of measure classes and units, where the source meters anything | Stage 0 | [usage-setup.md](../usage-consumption/usage-setup.md#manual-sequence-help-indum_configure_usage_records) (steps 1 and 2 come before the usage product, step 3) | [usage-consumption](../usage-consumption/SKILL.md) |
| 1 | Catalog: products, attributes, classifications, bundles, categories | Stage 0; units of measure, for usage products | [product-catalog-modeling](../product-catalog-modeling/SKILL.md) | [product-catalog-modeling](../product-catalog-modeling/SKILL.md) |
| 2 | Selling models and options per product | Catalog | [Quick Rules](../product-catalog-modeling/SKILL.md#quick-rules) (option per model) | [selling-models-and-lifecycle.md](../product-catalog-modeling/selling-models-and-lifecycle.md) |
| 3 | Price books and entries; cost books if used | Products, selling models (entries carry the model) | [Setup order](../pricing-setup/SKILL.md#setup-order), [price-books.md](../pricing-setup/price-books.md) | [pricing-setup](../pricing-setup/SKILL.md) |
| 3 | Adjustment schedules | Selling models and products in a price book | [Setup order](../pricing-setup/SKILL.md#setup-order), [price-adjustment-schedules.md](../pricing-setup/price-adjustment-schedules.md#set-it-up) (Help prerequisites) | [pricing-setup](../pricing-setup/SKILL.md) |
| 3 | Revision policies and index rates | Region picklist values on Index Rate (Help: add them first) | [price-revision-policies.md](../pricing-setup/price-revision-policies.md#set-it-up) (Help set-up order); Help names no price book prerequisite | [pricing-setup](../pricing-setup/SKILL.md) |
| 3 | Context definition, mappings, tags | Custom fields | [dependency-ordering.md](../repo-integration/dependency-ordering.md#pre-deploy-numbered-directories), [context-service](../context-service/SKILL.md) | [context-service](../context-service/SKILL.md) |
| 4 | Decision tables defined, data loaded, refreshed | Price books and source data they read | [Setup order](../pricing-setup/SKILL.md#setup-order), [The timing rule](../decision-tables/SKILL.md#the-timing-rule) | [decision-tables](../decision-tables/SKILL.md) |
| 4 | Recipe and table mappings | Decision tables | [Pricing Recipe Table Mappings](../pricing-wiring/SKILL.md#a-pricing-recipe-table-mappings), [Setup order](../pricing-setup/SKILL.md#setup-order) | [pricing-wiring](../pricing-wiring/SKILL.md) |
| 5 | Pricing procedure: elements, simulate, activate, set in revenue settings | Recipe, tables fresh, context tags | [Setup order](../pricing-setup/SKILL.md#setup-order), [Activation after a decision table change](../pricing-procedures/procedure-anatomy-and-ordering.md#activation-after-a-decision-table-change) | [pricing-procedures](../pricing-procedures/SKILL.md), [expression-sets](../expression-sets/SKILL.md) |
| 5 | Procedure plan, where used | The procedures it runs, active `[inferred]` (the repo's flow activates them first: `prepare_procedureplans` runs `activate_procedure_plan_expression_sets` before `create_procedure_plan_definition`) | [Procedure Plans and Overlays](../pricing-wiring/SKILL.md#c-procedure-plans-and-overlays), `cumulusci.yml` | [pricing-wiring](../pricing-wiring/SKILL.md) |
| 6 | Constraint models | Catalog bundles and their members; the context definition and any tags their rules read | [constraint-models](../constraint-models/SKILL.md) `[inferred]` | [constraint-models](../constraint-models/SKILL.md) |
| 6 | Approvals: matrix, flows, pricing flags | Pricing procedure for any level it calculates; notification content | [advanced-approvals](../advanced-approvals/SKILL.md), [What the repo ships](../advanced-approvals/SKILL.md#what-the-repo-ships) | [advanced-approvals](../advanced-approvals/SKILL.md) |
| 6 | Tax engine, tax policies and treatments, legal entity | Stage 0; catalog (the products a tax policy applies to) | [dependency-ordering.md](../repo-integration/dependency-ordering.md#data-dependencies) (tax loads before billing, which reads its legal entity), [tax.md](../billing-operations/tax.md), [accounting.md](../billing-operations/accounting.md) | [billing-operations](../billing-operations/SKILL.md) |
| 6 | Estimated tax on quotes and orders, where the source shows tax on quotes | A tax engine and tax policy set up first (Help); the repo's flow also requires an active policy and switches it on only after the tax data loads | [dependency-ordering.md](../repo-integration/dependency-ordering.md#prepare_rlm_org-step-ordering), `cumulusci.yml` (`deploy_quote_est_tax_settings`, flags `quote_est_tax` and `tax`), [Help: `ind.qocal_turn_on_quote_and_order_capture`] (set up a tax engine and policy first; after enabling, verify the tax attributes are mapped in the sales transaction context), [Pricing actions](../transaction-line-editor/runtime-behavior.md#4-pricing-actions) (Estimate Taxes needs the Revenue Setting) | [transaction-line-editor](../transaction-line-editor/SKILL.md) |
| 6 | Billing policies, treatments, payment terms | Catalog (products they apply to); a legal entity where a treatment is selected by it (shared with the tax row where both are built) | [Billing policies and treatments](../billing-setup/SKILL.md#billing-policies-and-treatments), [dependency-ordering.md](../repo-integration/dependency-ordering.md#data-dependencies) (in this repo's data, billing reuses tax's legal entity) | [billing-setup](../billing-setup/SKILL.md) |
| 6 | Fulfillment configuration | Catalog products it decomposes; context and rule resources it reads | [dro-plans Quick Rules](../dro-plans/SKILL.md#quick-rules) (parents before children), [authoring-and-deployment.md](../dro-plans/authoring-and-deployment.md) | [dro-plans](../dro-plans/SKILL.md) |
| 6 | Contract setup | Feature access, settings, then types and states, then content | [salesforce-contracts Quick Rules](../salesforce-contracts/SKILL.md#quick-rules) | [salesforce-contracts](../salesforce-contracts/SKILL.md) |
| 6 | Usage resources, product usage resources, grants, usage policies, commitments | The usage products and their units | [usage-setup.md](../usage-consumption/usage-setup.md#manual-sequence-help-indum_configure_usage_records) (steps 4 to 10; step 11 links sold assets, stage 10) | [usage-consumption](../usage-consumption/SKILL.md) |
| 6 | Rate cards, entries, price book rate cards, rating procedure | Usage resources; the products and selling models the entries name; price book; then the decision tables rating reads, refreshed | [rate-management Quick Rules](../rate-management/SKILL.md#quick-rules) (1, 2, 5, 7) | [rate-management](../rate-management/SKILL.md) |
| 7 | Quote and order UI, line editor, quote and order documents (contract documents go with contract setup, stage 6) | Catalog; each custom line-editor column in the sales transaction context; templates after their data mappers `[inferred]` (a template references its mappers by name, `document-generation` Quick Rule 1) | [transaction-line-editor](../transaction-line-editor/SKILL.md), [document-generation](../document-generation/SKILL.md) | same |
| 8 | First transaction: quote, price, place | Stages 3 to 6 as the deal requires | [rlm-business-apis](../rlm-business-apis/SKILL.md#transaction-lifecycle-apis) | [rlm-business-apis](../rlm-business-apis/SKILL.md) |
| 9 | Order activation, fulfillment, billing schedules, assets | Placed order; fulfillment and billing configuration, including the billing context definition and mapping; the order's bill-to contact and addresses | [authoring-and-deployment.md](../dro-plans/authoring-and-deployment.md), [billing-operations Quick Rules](../billing-operations/SKILL.md#quick-rules) (1: schedules at activation) | [dro-plans](../dro-plans/SKILL.md), [billing-setup](../billing-setup/SKILL.md), [billing-operations](../billing-operations/SKILL.md) |
| 10 | Lifecycle changes: amend, swap, cancel, renew | An asset exists | [asset-lifecycle-changes](../asset-lifecycle-changes/SKILL.md), [renewal-asset-creation](../renewal-asset-creation/SKILL.md) | same |
| 10 | Usage recording and rating | A usage-entitled asset; for a commitment, each commitment asset linked to its anchor asset after activation (without the link the commitment is inert) | [The Pipeline](../usage-consumption/SKILL.md#the-pipeline), [usage-consumption Quick Rules](../usage-consumption/SKILL.md#quick-rules) (5) | [usage-consumption](../usage-consumption/SKILL.md) |
| 10 | Invoice runs, tax, payments and credits | Billing schedules; the tax engine, where tax is in scope; the legal entity | [billing-operations Quick Rules](../billing-operations/SKILL.md#quick-rules) (2: invoices come from schedules; 5: tax engine; 7: legal entity) | [billing-operations](../billing-operations/SKILL.md) |

Edges the skills state only for one domain, and not as part of a cross-domain graph, are
listed above with their source. Edges the table marks `[inferred]`, and any edge between
stages 6 and 9 that neither this table nor an owner skill states (for example what billing
needs from fulfillment), are not established: log them as open and verify live.

### Refresh and activation triggers

A change in one domain makes lookups in another stale. Plan a refresh after each:

| After changing | Refresh or reactivate | Source |
|---|---|---|
| Products, price book entries, rates, contracts feeding a table | The decision tables that read them | [decision-tables](../decision-tables/SKILL.md), [Freshness](../decision-tables/SKILL.md#freshness--what-the-verdicts-mean) |
| A decision table definition | The procedure that uses it: after the table, make a small change to the procedure, save, then activate (Help) | [Activation after a decision table change](../pricing-procedures/procedure-anatomy-and-ordering.md#activation-after-a-decision-table-change) |
| Newly loaded catalog content | The decision tables and the catalog search index, then wait for the index build; which of the two Place needed is not shown (traced in part: no search-index dependence was found) | [PCM load facts](../product-catalog-modeling/catalogs-and-loading.md#pcm-load-facts-264) (fact f) |
| Loading rating records (product usage resources, grants) | Activate them in dependency order | [dependency-ordering.md](../repo-integration/dependency-ordering.md#post-load-activation-patterns) |
| Rate data | The decision tables rating reads; wait until they are no longer stale | [rate-management Quick Rules](../rate-management/SKILL.md#quick-rules) (7) |

Refresh a table when its source criteria become true, not when the source row is written
([The timing rule](../decision-tables/SKILL.md#the-timing-rule)).

## Cross-check against this repo's flow

The repo realizes a subset of the graph as the `prepare_rlm_org` flow in `cumulusci.yml`,
documented in
[dependency-ordering.md](../repo-integration/dependency-ordering.md#prepare_rlm_org-step-ordering).
Use it to corroborate an edge (it shows one order that works, not that the order is
required), never as the customer plan. Steps are cited by flow or task
name, never by number, so `tests/test_doc_build_steps.py`, which tracks numeric step
citations, has nothing here to track.

| Graph stage | Realized by | Notes |
|---|---|---|
| 0, 1, 3 (settings, fields; context definitions) | `prepare_core` | Settings, licenses, context definitions and their domain extensions, and pre-deploy metadata come first; a few context overlays (docgen, billing order, constraints, approvals, PRM) run later, in their domain's sub-flow |
| 4 (tables) | `prepare_core` (`deploy_pre` deploys the definitions), `prepare_decision_tables` (activates them), then `refresh_all_decision_tables` late | The full refresh runs after all data is loaded |
| 4 (recipe mappings) | `configure_core_pricing_recipe_table_mappings`, inside `prepare_expression_sets` | |
| 5 (procedures) | `prepare_expression_sets`, then `activate_and_deploy_expression_sets` | Deploy early; activation after data and rating |
| 1, 2 (catalog) | `prepare_product_data` | After `deploy_full` and the schedule activation |
| 3 (prices) | `prepare_price_adjustment_schedules`, `prepare_pricing_data` | Existing schedules are activated before the catalog loads (some stay inactive on purpose); the adjustment records load with the pricing data after it |
| 5 (revenue settings) | `prepare_revenue_settings` | Runs late, after constraints and guided selling |
| 6 (fulfillment) | `prepare_dro` | After pricing data |
| 6 (tax) | `prepare_tax` | Before billing; billing reads its legal entity. It also turns estimated tax on when the `quote_est_tax` and `tax` flags are on and an active tax policy exists; on a fresh org `prepare_core` leaves it off, since no active policy exists yet |
| 6 (billing, usage) | `prepare_billing`, `prepare_rating` | The flow runs rating after billing; the rating data plan loads its own usage resource billing policies (`datasets/sfdmu/qb/en-US/qb-rating/README.md`) |
| 5 (procedure plans) | `prepare_procedureplans` | After expression-set activation and the approvals pricing overlay |
| 6 (contracts) | `prepare_clm` | |
| 6 (approvals) | `prepare_approvals` (within `prepare_quantumbit`), then `prepare_approvals_pricing` | Fields, flows, orchestration and alert data deploy before the catalog; the level bands (the approval-flags overlay) come after expression-set activation |
| 6 (constraints) | `prepare_constraints` | After the catalog |
| 7 (documents) | `prepare_docgen` | Runs early, right after pricing data and before fulfillment |
| 7 (UX) | `prepare_ux` | Runs late, after objects and pages exist |
| Refresh triggers (before stage 8) | `refresh_all_decision_tables`, then `rebuild_search_index` | End of build, after all data loads; `prepare_pricing_discovery` runs earlier, after revenue settings |

The flow is ordered for one scripted build, so it also contains repo-specific items (demo
catalog, personas, in-app learning, agents, community) that no customer graph needs unless
asked. Where the flow and the graph disagree, the flow likely reflects a repo constraint
(for example shared sample data) `[inferred]`. Order differs too:

- Context definitions and most of their extensions deploy with the core settings in the
  flow but sit at stage 3.
- Decision table definitions deploy and activate, recipe mappings are configured, and
  procedures deploy, before the catalog
  and price books in the flow but sit at stages 4 and 5.
- The flow activates existing price adjustment schedules before the catalog loads and loads
  their adjustment records with the pricing data after it; the graph puts schedules after
  the catalog.
- Approval metadata and data deploy before the catalog in the flow but sit at stage 6.
- Documents are built early in the flow but sit at stage 7.
- Revenue settings are set late in the flow but sit at stage 5.
- Procedures are activated and procedure plans built after the stage 6 data (tax, billing,
  rating) in the flow but sit at stage 5.

Decide per plan and record why.

To re-verify the cross-check when the flow changes, list its steps (`cci flow info
prepare_rlm_org`) or read the flow in `cumulusci.yml`, and compare names.

## Parallelism and gates

- Stages 3 and 6 include items with no recorded edge between them `[inferred]` (others have
  one, in their Needs cells); assign them to separate workers only when each
  owner's prerequisites are met.
- A stage's exit check is the owner's org-verification checks where it has them (an owner
  with none is an open item, logged), not the stage's completion in
  tooling. Do not start a stage that depends on a table or procedure until the freshness
  and activation checks pass.
- Record each edge you rely on that is `[inferred]` or open in the decision log.
