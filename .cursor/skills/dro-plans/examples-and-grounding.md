# DRO Examples and Grounding Sources

## Source Hierarchy

Use target org describes/settings and observed runtime results as ground truth.
The linked Salesforce Help corpus explains administrator behavior;
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

### QuantumBit Decomposition Reference

The shipped QuantumBit `qb-dro` records show `QuantumBit Services Project`
(`QB-BDL-SRVC`) decomposing to `Project Service` (`QB-DRO-PROJ`) and `Finance`
(`QB-DRO-BILL`). This is a repository example, not a required product design.
The [worked decomposition extension](csv-and-sfdmu.md#worked-decomposition-extension)
shows the general source/destination relationships and scenario binding pattern;
replace its illustrative keys with unique records from the target catalog.

Reuse suitable catalog products, preserve commercial pricing and usage settings,
and verify generated source relationships. Review source and destination scenario
eligibility to prevent duplicate work. The worked example is not live-verified;
follow the evidence report below for each target.

### Live QuantumBit Bundle Smoke

[Measured: smoke, API 68.0, one org, run date not recorded (the file's first
commit is 2026-10-15), release and org type not recorded] A separate smoke test
verified this decomposition pattern against a target org. An isolated Add scenario on the commercial service bundle was composed
alongside the existing scenarios on its two technical destinations. The transaction
harness expanded the configurable bundle into commercial `OrderItem` components;
after activation, DRO generated two technical `FulfillmentOrderLineItem` records.
Their `OrderItemId` values were null, while `FulfillmentLineSourceRel` linked each
back to the source bundle line. Inspect commercial bundle expansion and DRO technical
decomposition separately, because only the commercial lines carried an order item.

The composed plan contained eight steps, including the two new bundle-level
milestones and the existing project and finance work. Runtime dependency records
linked each configured dependent step to its intended predecessor. DRO reported
decomposition and composition complete, and the harness completed its activation,
billing-schedule, and asset checkpoints while the plan stayed InProgress. The two
added milestones auto-completed, and existing manual and billing steps remained
open. This verifies configuration, composition, and order activation in
that target; it does not verify end-to-end fulfillment, repeat-load idempotency,
or portability to another org. The temporary dataset was loaded directly through
SFDMU after simulation because no CCI alias was available; CCI-only preprocessing
such as dynamic assignee replacement was not exercised.

Open contradiction: the captured Help article for the order orchestration template
says users complete manual tasks and milestones in the plan, whereas two measurements,
each on one org (the smoke and the recheck below), saw milestones complete without a user;
do not model a human acceptance as a Milestone on this evidence. Confirm on a live
target, and treat a person's sign-off as a manual task unless a run shows otherwise
[inferred]. In both runs activation created the assets and billing schedules before the
plan finished, so plan the installed base and billing from activation, not from a step
[inferred].

#### Recheck

[Measured: 2026-11-13, 264, scratch, one org] A repeat on one scratch org carrying the
shipped DRO configuration plus additive test step definitions, a test product and a
scenario, run through order creation and activation by API:

- Assets and billing schedules were created at activation, before any step ran. A
  Milestone step with no unmet dependency completed within about a second with nobody
  acting; a Milestone behind an incomplete predecessor stayed Pending. Manual steps
  waited for a user and the plan stayed InProgress. That matches the smoke and still
  contradicts Help's wording.
- Technical fulfillment lines had a null `OrderItemId`, each linked to its source line
  by `FulfillmentLineSourceRel`.
- A Callout step whose named credential was missing went FatallyFailed and blocked every
  dependent step; the plan stayed InProgress (advice: check credentials before a smoke).
- Activating the order failed until it had a bill-to contact and a shipping address;
  order creation from a quote filled the billing address but not the contact.

## Checks When Using the Examples

| What to check | How to handle it |
| --- | --- |
| The captured schema and object guide disagree on supported step `Scope` values | Use target picklists; do not reject values from incomplete documentation |
| Captured step/scenario `UsageType` includes `Fulfillment`, whereas the step object guide lists `OrderFulfillment`; scenario Action capture uses `No Change` while guide lists `NoChange` | Use exact target API values, not guessed label normalization |
| Captured step rule lookups include `Ruleset` and `ExpressionSet`; object guide lists only `ExpressionSet` | Inspect actual `referenceTo` and generated condition references |
| Several shipped/placeholder rules match by autonumber Name | Do not copy that matching strategy; establish a semantic identity or use targeted target-ID updates |
| Shipped export omits some condition, execution-user and advanced fields | Extend a reviewed export plan before claiming a complete round trip; do not align away custom fields |
| A context field used to group custom scopes has an incompatible datatype | Verify tag datatype. A custom String attribute/tag/mapping is needed where required; selecting a context alone does not correct datatype |
| Repository creates `RLM_SalesTransactionContext` but the QB README records selected-context assignment as outstanding | Discover actual DRO settings; extension creation is not proof of selection |

## Captured Article Map

The local links below point to the repository's captured Salesforce documentation.
They are a reference snapshot, not a live-org verification; use the matching release
articles and target describes when behavior differs or the target uses another release.
The `264` in these paths is the snapshot captured when this table was written; substitute
the active release from `.claude/skill-manifest.yml` (`salesforce_release_active`).

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
| Future-dated step execution | [Steps for future execution](../../../docs/salesforce/264/help/articles/ind.dro_configure_steps_for_future_execution.htm.md), [turn on future-dated steps](../../../docs/salesforce/264/help/articles/ind.dro_turn_on_future_dated_steps.htm.md) |
| Point-of-no-return state propagation | [PONR state propagation](../../../docs/salesforce/264/help/articles/ind.dro_point_of_no_return_state_propagation.htm.md) |
| Jeopardy and SLA | [Jeopardy rules](../../../docs/salesforce/264/help/articles/ind.dro_configure_fulfillment_step_jeopardy_rules.htm.md), [SLA jeopardy administration](../../../docs/salesforce/264/help/articles/ind.dro_sla_jeopardy_administration.htm.md) |
| Retries and fallout | [Step retries](../../../docs/salesforce/264/help/articles/ind.dro_configure_fulfillment_step_retries.htm.md), [fallout rules](../../../docs/salesforce/264/help/articles/ind.dro_configure_fallout_rules.htm.md), [fallout design](../../../docs/salesforce/264/help/articles/ind.dro_fallout_design_and_management.htm.md) |
| Scenario actions and in-flight order changes | [Configure scenarios](../../../docs/salesforce/264/help/articles/ind.dro_configure_scenarios_for_a_fulfillment_step_definition_group.htm.md), [how in-flight changes decompose](../../../docs/salesforce/264/help/articles/ind.dro_how_in_flight_order_changes_decompose.htm.md) |
| Time-awareness | [Turn on time-awareness](../../../docs/salesforce/264/help/articles/ind.dro_time_aware_fulfillment_enable.htm.md) |
| Backdated changes | [Backdated changes](../../../docs/salesforce/264/help/articles/ind.dro_considerations_for_backdated_changes_in_dynamic_revenue_orchestrator.htm.md) |
| Limits | [DRO limits](../../../docs/salesforce/264/help/articles/ind.dro_dynamic_revenue_orchestrator_limits.htm.md) |
| Orchestration template | [Order orchestration template](../../../docs/salesforce/264/help/articles/ind.dro_hi_tech_order_orchestration_template.htm.md) (says users complete milestones; see the open contradiction above) |
| Fulfillment step types | Capture gap: the snapshot only links the step-types article (from [Define a step](../../../docs/salesforce/264/help/articles/ind.dro_define_a_fulfillment_step.htm.md)); use the target's picklist |

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
