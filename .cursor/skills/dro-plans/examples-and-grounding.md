# DRO Examples and Grounding Sources

## Source Hierarchy

Use target org describes/settings and observed runtime results as ground truth
for pre-GA Release 264. The captured Help corpus explains administrator behavior;
the Developer Guide explains APIs/deployment; the ERD and schema capture provide
object relationships. Neither a sample CSV nor an old README establishes a
universal platform rule. Read [revenue-cloud-docs](../revenue-cloud-docs/SKILL.md)
before authoring new product claims. Never relabel or modify captured articles
to resolve a discrepancy; record it here or in the deployment evidence.

## Repository Examples

Discover shipped datasets and task options rather than hardcoding their records:

```bash
rg --files datasets/sfdmu | rg '/[^/]*dro/(export.json|README.md)$'
rg -n 'prepare_dro:|insert_qb_dro_data:|extract_qb_dro_data:|manage_fulfillment_scope_cnfg:' cumulusci.yml
```

The [qb-dro dataset](../../../datasets/sfdmu/qb/en-US/qb-dro/README.md) contains
the main populated example: decomposition rules, groups, steps, dependencies,
scenarios, workspaces, fallout and jeopardy rules. Inspect its files to discover
the current configuration.
The [q3-dro dataset](../../../datasets/sfdmu/q3/en-US/q3-dro/README.md) currently
has empty orchestration CSVs and is not evidence of a functioning Q3 plan.

`prepare_dro` manages custom scopes before its family-specific dataset load and
performs additional build-wide operations. Context extension and rule-library
creation occur earlier elsewhere in the build. The scope seed is
[CustomFulfillmentScopeCnfg.json](../../../datasets/tooling/CustomFulfillmentScopeCnfg.json);
the [scope task](../../../tasks/rlm_manage_fulfillment_scope_cnfg.py) exposes
list/extract/upsert and dry-run options. The
[loader](../../../tasks/rlm_sfdmu.py) provides simulation and dynamic-user handling.
Do not run `prepare_dro` as a generic scoped deployment: it selects sample families
and includes updates to every decomposition rule.

### Follow the Shipped Services Chain

The `qb-dro` CSVs illustrate `Create Project` (Milestone) → `Assign Resources`
(ManualTask) → `Start Project` (Milestone), followed by `Initiate Billing` in
Finance. The first two definitions use LineItem scope; the last two use Plan
scope. Inspect the definition, dependency and scenario CSVs together, then query
the target to establish what is actually deployed.

The shipped dependency rows use Plan scope, including edges whose predecessors
use LineItem scope. Help instructs matching dependency scope to the predecessor's
scope. Treat this as a sample/documentation discrepancy requiring target runtime
verification; do not copy the sample's scopes blindly. For independent service
lines, the worked CSV example uses LineItem on both steps and their dependency.
A callout can run independently when it has no dependency edges; chain only the
steps whose business prerequisites require it.

### Generic Services Decomposition

A commercial services line can produce a technical Project Service item, with
an optional second Billing Setup item. The
[worked decomposition extension](csv-and-sfdmu.md#worked-decomposition-extension)
shows technical-product creation, source/destination references, a decomposition
rule, and a scenario selecting the technical item's step group.

Choose technical outcomes from the requested fulfillment work. Reuse catalog
products when suitable, preserve commercial pricing and usage configuration,
and verify the generated source relationships. Adding a technical scenario while
leaving the same work on the commercial scenario can compose duplicate work;
review eligibility before deploying. These examples have no live verification
claim; follow the evidence report below for each target.

## Checks When Using the Examples

| What to check | How to handle it |
| --- | --- |
| Captured 264 step `Scope` includes `Custom`; its object guide lists only Plan/Bundle/LineItem/CrossPlan | Use target picklists; do not reject Custom from incomplete documentation |
| Captured step/scenario `UsageType` includes `Fulfillment`, whereas the step object guide lists `OrderFulfillment`; scenario Action capture uses `No Change` while guide lists `NoChange` | Use exact target API values, not guessed label normalization |
| Captured step rule lookups include `Ruleset` and `ExpressionSet`; object guide lists only `ExpressionSet` | Inspect actual `referenceTo` and generated condition references |
| Several shipped/placeholder rules match by autonumber Name | Do not copy that matching strategy; establish a semantic identity or use targeted target-ID updates |
| Shipped export omits some condition, execution-user and advanced fields | Extend a reviewed export plan before claiming a complete round trip; do not align away custom fields |
| Fresh 264 `SalesTransactionItemGroup` is Lookup; custom scopes require String | Verify tag datatype. A custom String attribute/tag/mapping is needed for group-based scope; selecting the RLM context alone does not fix the datatype |
| Repository creates `RLM_SalesTransactionContext` but the QB README records selected-context assignment as outstanding | Discover actual DRO settings; extension creation is not proof of selection |

## Authoritative Article Map

These references cover Release 264. Each article links to its Salesforce source.
Check the target release's documentation when behavior is uncertain.

| Topic | Local source |
| --- | --- |
| Deployment object sequence and lookups | [DRO objects](../../../docs/salesforce/264/dev-guide/articles/deployment_dynamic_revenue_orchestrator_objects.htm.md) |
| Settings, context nodes and permissions | [DRO metadata](../../../docs/salesforce/264/dev-guide/articles/deployment_dynamic_revenue_orchestrator_metadata.htm.md) |
| Condition lifecycle, library versioning, migration, DT refresh | [Additional deployment information](../../../docs/salesforce/264/dev-guide/articles/deployment_dynamic_revenue_orchestrator_additional_info.htm.md) |
| Step types, scope, execution user | [Define a step](../../../docs/salesforce/264/help/articles/ind.dro_define_a_fulfillment_step.htm.md), [step object fields](../../../docs/salesforce/264/dev-guide/articles/sforce_api_objects_fulfillmentstepdefinition.htm.md) |
| Dependency direction/scope and propagation | [Dependencies](../../../docs/salesforce/264/help/articles/ind.dro_set_dependencies_between_fulfillment_steps.htm.md), [dependency object](../../../docs/salesforce/264/dev-guide/articles/sforce_api_objects_fulfillmentstepdependencydef.htm.md) |
| Product/classification/order scenarios | [Configure scenarios](../../../docs/salesforce/264/help/articles/ind.dro_configure_scenarios_for_a_fulfillment_step_definition_group.htm.md) |
| Decomposition priorities and naming | [Product decomposition](../../../docs/salesforce/264/help/articles/ind.dro_define_how_a_product_decomposes.htm.md) |
| Technical catalog, activation, assetizability and quantity | [Model technical products](../../../docs/salesforce/264/help/articles/ind.dro_technical_product_in_dro.htm.md), [create a technical product](../../../docs/salesforce/264/help/articles/ind.dro_creating_a_technical_product.htm.md) |
| Grouping generated fulfillment lines | [Decomposition scope](../../../docs/salesforce/264/help/articles/ind.dro_decomposition_scope.htm.md) |
| Linking generated lines to their source | [Fulfillment line source relationship](../../../docs/salesforce/264/dev-guide/articles/sforce_api_objects_fulfillmentlinesourcerel.htm.md) |
| Enrichment fields and calculation dependencies | [Enrichment object](../../../docs/salesforce/264/dev-guide/articles/sforce_api_objects_productdecompenrichmentrule.htm.md) |
| Custom scope tags, mappings, datatype and fallback | [Custom scopes](../../../docs/salesforce/264/help/articles/ind.dro_create_custom_scope_config.htm.md) |
| Condition evaluation/branch skip | [Step conditions](../../../docs/salesforce/264/help/articles/ind.dro_define_conditions_for_a_fulfillment_step_to_run.htm.md) |
| Submission | [Submit Sales Transaction action](../../../docs/salesforce/264/dev-guide/articles/actions_obj_submit_sales_transaction.htm.md) |
| Freeze/unfreeze | [Freeze action](../../../docs/salesforce/264/dev-guide/articles/actions_obj_freeze_sales_transaction.htm.md), [unfreeze action](../../../docs/salesforce/264/dev-guide/articles/actions_obj_unfreeze_sales_transaction.htm.md) |
| Compensation, PONR and Frozen requirements | [In-flight considerations](../../../docs/salesforce/264/help/articles/ind.dro_considerations_for_changing_in_flight_orders.htm.md), [step settings](../../../docs/salesforce/264/help/articles/ind.dro_configure_inflight_plan_settings.htm.md) |
| Runtime monitoring, completion and retry | [Plan actions](../../../docs/salesforce/264/help/articles/ind.dro_fulfillment_plan_actions_and_information.htm.md) |

## Evidence Report

For each deployment, record the target/release, configuration roots/keys, source
articles/schema and any discrepancies, prerequisites, exact change scope, loader
results, before/after read-back, repeat-load results, and tested transactions.
State separately whether configuration, runtime composition and end-to-end execution
passed. For missing tests, identify the unavailable org/credential/operator action
and the next verification required; do not convert an expected result into a claim.

The CSV worked example and procedures in this skill are documentation artifacts.
Offline validation establishes formatting/discovery and consistency with repository
sources; it does not establish successful live load or fulfillment.
