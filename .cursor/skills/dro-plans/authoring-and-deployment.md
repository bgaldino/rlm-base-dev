# Authoring and Deploying DRO Configuration

## 1. Resolve the Target and Existing State

Use an explicit target for every operation. CCI and SF CLI have different alias
registries: resolve both to the same username/org ID before loading. Do not print
access tokens; CLI commands take aliases/usernames, never tokens. Read
[CCI orchestration](../cci-orchestration/SKILL.md) for registry/task mechanics.

If CCI cannot discover the checkout, follow the worktree/project-discovery
guidance in [CCI orchestration](../cci-orchestration/SKILL.md); do not alter Git
metadata or point CCI at another checkout.

```bash
SF_ORG="your-sf-alias-or-username"
CCI_ORG="your-cci-alias"
sf sobject describe --sobject FulfillmentStepDefinition --target-org "$SF_ORG" --json
sf sobject describe --sobject ProductFulfillmentScenario --target-org "$SF_ORG" --json
sf data query --target-org "$SF_ORG" --query "SELECT Id, Name, UsageType FROM FulfillmentStepDefinitionGroup"
sf data query --target-org "$SF_ORG" --query "SELECT Id, Name, StepDefinitionGroupId, StepType, Scope FROM FulfillmentStepDefinition"
sf data query --target-org "$SF_ORG" --query "SELECT Id, Name, FulfillmentStepDefinitionId, DependsOnStepDefinitionId, DependencyScope FROM FulfillmentStepDependencyDef"
cci task run manage_fulfillment_scope_cnfg --org "$CCI_ORG" -o operation list
```

Describe every object/field the change uses, not just those examples. Confirm
API version and whether the org is fresh or upgraded. Inspect DRO settings in
Setup or their supported metadata surface: enabled DRO, fulfillment user,
selected sales/asset context and node bindings, optional in-flight amendments,
future-dated steps, fallout and SLA. Do not enable optional features unrelated
to the request. Read the corresponding Help article before changing a setting.

Settings checklist (copy, mark each on, off or n/a for the target):

- [ ] Dynamic Revenue Orchestrator on [Help: ind.dro_turn_on_dynamic_revenue_orchestrator]
- [ ] Fulfillment user set; holds DRO Admin User or Submit Transactions and Fulfillment User, plus Assetize Order when assetization is automatic (the submitting user needs it too) [Help: ind.dro_add_a_fulfillment_user]
- [ ] In-Flight Amendments, only if amend or cancel of active plans is in scope [Help: ind.dro_enable_in_flight_amendments]
- [ ] Future-Dated Steps, only if a step has an execution schedule [Help: ind.dro_turn_on_future_dated_steps]
- [ ] Fallout and SLA features, only if fallout, retries or jeopardy are in scope [Help: ind.dro_turn_on_features_to_manage_fallout_and_service_level_agreements].
  This repo's settings metadata turns both on but creates neither decision table. Switch each
  off and on in Setup > Dynamic Revenue Orchestrator > Fallout and SLA Settings, then check that
  both tables exist and are Active (step 5 below) [Measured: 2026-11-16, 264, scratch, one org;
  repeated 2026-11-17 on a second org]
- [ ] Time-awareness, only after the migration it names and for backdated or future-dated changes [Help: ind.dro_time_aware_fulfillment_enable]
- [ ] Rule library named `DRORuleLibrary` for the default usage type [Help: ind.dro_orchestrate_a_business_process]
- [ ] Selected sales transaction context and node bindings: Setup > Dynamic Revenue Orchestrator > Context Definition Settings, Setup-only fields with no metadata route [Dev guide: deployment-dynamic-revenue-orchestrator-metadata; Help: ind.dro_associate_custom_context_definition_with_sales_transaction_attribute].
  A fresh build of this repo leaves the standard `SalesTransactionContext__stdctx` selected
  [Measured: 2026-11-16, 264, scratch, one org]. Switch it only when DRO must read a tag of the
  extended context, such as a Custom Date step; the procedure is in section 3

Discover product/classification matches, technical-product activation, attributes,
active flows/providers, credential access, users/queues, scenarios and workspace
membership. Query existing requests/plans when updating configuration. An empty
query result must not be confused with inaccessible objects or missing permissions.

## 2. Turn the Requirement into a Graph

Record the intended transaction actions, source products/classifications, technical
outputs/quantities, steps, condition resources, scopes, assignees/execution users,
dependencies, and expected step count for a representative order. Reuse existing
products and prerequisites when suitable. General catalog authoring belongs to an
upstream change; new technical-product creation can be explicitly scoped into the
fulfillment dataset. Do not invent decomposition when direct fulfillment is sufficient.

Use the [object graph](objects-and-relationships.md) to select records. Check:

- **Decomposition:** source versus destination, classification/product overlaps,
  priorities, technical bundles and scopes. Lower priority numbers win when rules
  write to the same destination; modification time breaks ties per Help. Avoid
  unintended ties and decomposition-rule names containing `>`; reject cyclic paths.
- **Steps:** type-specific fields. `AutoTask` needs its active Flow;
  `Callout` needs its integration provider; successful execution also needs usable
  credentials and a working endpoint/response contract;
  `ManualTask` needs suitable assignment and no callout provider. A manual step assigned to
  a queue with no `TaskAllocationType` was refused with "Step Assignment Method is invalid";
  `RoundRobin` was accepted and handed each step to a queue member, so the build gave every
  queue a member [Measured: 2026-11-17, 264, scratch, one org]. `Milestone`,
  `Pause`, and `StagedAssetize` need their own documented execution behavior.
  An explicitly requested callout-failure demonstration can omit its credential;
  document the expected failure and verify its actual state before claiming it works.
- **Scopes:** Plan/Bundle/LineItem/custom scope, instance multiplicity, and scope
  of each predecessor. Dependency direction is dependent → depends-on predecessor.
  Validate the combined graph, including existing edges, for self-edges/cycles.
- **Scenarios:** product, classification or order-wide eligibility, actions, group
  and conditions. Verify product-specific versus classification precedence and
  overlapping scenarios against expected composition. For order-wide behavior,
  follow Help's Plan-scope guidance; do not invent a scenario field from a UI label.
- **Optional features:** delays/custom dates
  ([updates-and-runtime.md](updates-and-runtime.md)), branch skipping, cross-plan
  prerequisites, amend/cancel groups, Point of No Return and reverse compensation.

Custom scope tags must resolve to String attributes in the selected context, with
the appropriate OrderItem and/or fulfillment-line mappings. Read
[context-service](../context-service/SKILL.md) before changing nodes/tags/mappings.
The scope task's `dry_run` does not establish that the server accepts the tag type.

Verify a custom scope exists before loading its consumers. Read back both
`Product2.DecompositionScope` and `CustomDecompositionScope`, plus each step's
`CustomFulfillmentScope`. Products can lose their decomposition settings when a
scope is missing, while steps can retain an unresolved scope name. After correcting
the scope, restore the intended product fields and repair the step references.

### Decomposed Line Items

The order's commercial `OrderItem` and the UI's **Decomposed Line Items** are
different records. A quote/order bundle can first expand into commercial component
`OrderItem` records; that catalog expansion is separate from DRO's technical
decomposition. A DRO decomposition rule maps a commercial product to a technical
`Product2`; submission generates `FulfillmentOrderLineItem` records and source
relationships. Count and inspect both layers independently. A fulfillment scenario
alone can select steps without generating technical outputs. Do not insert runtime
lines to fill an empty UI panel.

1. Specify the required technical outcomes and expected lines per source line.
   Reuse suitable technical products; create new ones through an upstream
   catalog dataset or explicitly scoped creation.
   Keep their pricing/usage significance separate from the commercial product.
2. Confirm destinations are active. Choose assetizability, decomposition scope,
   and quantity behavior deliberately. `OrderLineItem` with `AlwaysOne` is a
   useful service example: one technical item of quantity one per source line,
   even if the commercial line's quantity is ten. `Aggregate` serves a different
   quantity requirement. Product decomposition scope controls technical-item
   grouping; step `Scope` controls step multiplicity. Don't give a bundle child a scope
   broader than its parent's; from broad to narrow the scopes run Account, Order, Bundle,
   Order Line Item [Help: ind.dro_decomposition_scope]. Whether that warning reaches
   technical outputs decomposed from a bundle's components is unmeasured.
3. Create `ProductFulfillmentDecompRule` records using verified source and
   destination SKUs, unique names, and priorities. One source can have two rules
   for two distinct technical outcomes. Check inherited classification rules,
   conditions, destination overlaps, and cycles before adding another rule.
4. Decide where scenarios apply. To orchestrate the decomposed item, bind the
   intended group to the technical destination. When moving an existing direct
   scenario, update its discovered ID and preserve its identity. Review other
   source/classification/destination scenarios so the same project work is not
   selected twice. Separate commercial-level work can remain when intentional.
   A step definition belongs to one group: `StepDefinitionGroupId` is a required single
   lookup [Measured: 2026-11-13, 264, scratch, one org; describe]. A scenario binds one
   group to a product, so every step in that group is composed for the item unless a step
   condition skips it [inferred from the schema]. Give each technical item its own group of
   steps; a step that several items need with different predecessors needs one definition
   in each item's group. The same holds for one item fed by several source products whose
   work waits on different predecessors: a separate technical item, or one definition per
   case with a condition on the source product [inferred]. A shared step definition's
   dependency applies to every line the item carries, so it can't make one product's steps
   wait on a step only another product has [inferred]. A build moved that product to its
   own technical item [Measured: 2026-11-18, 264, scratch, one org], so its steps can wait
   on that other product's step [inferred]; a per-product definition with its own
   condition and dependency is untested.
   Count groups and step definitions before step instances.
5. If two outputs have separate groups, design dependencies between their actual
   instances. Do not copy a per-line dependency and assume it pairs different
   technical outputs. Discover source linkage and apply the documented scope
   rules; verify both standalone and combined orders.

For an empty Decomposed Line Items panel, inspect source-product/rule matching,
destination activation, condition evaluation, scope grouping, and the submission
request's decomposition status. A broad Order/Account scope can consolidate
outputs; do not assume an expected per-line count under that scope. Read back
destination settings after loading. Help's **None** choice means default behavior,
not a literal `None` API picklist value.

Before activating a test order, fill its bill-to contact and shipping address: activation
was refused without them, and creating the order from a quote filled the billing address
but not the contact [Measured: 2026-11-13, 264, scratch, one org]. The
[recheck](examples-and-grounding.md#recheck) lists what else that run showed.

On an authorized fresh test order, verify generated product IDs, quantities,
source relationships, steps, and edges—not just counts. `FulfillmentOrderLineItem.OrderItemId`
can be null on generated technical lines; use `FulfillmentLineSourceRel` to trace
each fulfillment line to its source `OrderItem` or prior fulfillment line.
Configuration changes do not retrofit a submitted plan. Respect a user's choice
to test manually and report runtime generation as unverified until evidence is
available. See the
[CSV extension](csv-and-sfdmu.md#worked-decomposition-extension) and
[technical-product sources](examples-and-grounding.md#captured-article-map).

## 3. Conditions and Rule Libraries

Author conditions through the supported UI or reuse verified condition
JSON from a matching schema/context. Inspect attribute codes, picklist names, and
context tags; remap source-specific IDs. A valid JSON document alone does not prove
that its expression evaluates correctly.

The condition fields are `ProductFulfillmentDecompRule.ConditionData`,
`ProductFulfillmentScenario.ConditionData`,
`FulfillmentStepDefinition.ExecuteOnConditionData` / `ResumeOnConditionData`, and
`FulfillmentTaskAssignmentRule.ConditionData`. Treat their generated RuleSet
references as verification outputs; explicit ExpressionSet references are a
separate supported design choice. Read
[expression-sets](../expression-sets/SKILL.md) for those procedures.

Discover the active Dfo context rule library/version and compare its context to
DRO's selected context. When changing the library's context, follow the documented
version lifecycle: clone the **latest** version, preserve rule sets, deactivate
the older version, then activate the replacement. Use the existing configured
library rather than creating another because a sample uses a different name.

Switching DRO's selected context, as measured [Measured: 2026-11-16, 264, scratch, one org;
repeated 2026-11-17 on a second org]:

1. Setup > Dynamic Revenue Orchestrator > Context Definition Settings > Sales Transaction
   Context Definition: pick the new context, then the header node. That unlocks the child
   nodes, each reset to unselected; set each again (on the repo's extended context, to its
   namesake). Save.
2. The optional Orchestration Group Key wasn't offered on the extended context and was left
   blank. It groups orders for cross-plan dependencies [Help: ind.dro_cross_plan_dependencies].
3. Clone the library's latest version onto the new context, deactivate the old version, then
   activate the new one. Check with
   `SELECT Name, Status, ContextDefinitionName FROM RuleLibraryVersion`.
4. The library record's own context name kept the old value; only the versions carry the new one.
5. Rerun one existing order and check its composition. Configuration with no condition JSON
   kept composing after the switch (one order); conditions bound to the old version weren't tested.

Condition JSON, as a UI-made rule saved it and as API writes in the same shape evaluated
[Measured: 2026-11-17, 264, scratch, one org]:

```json
{"Rules":[{"SequenceNumber":"1","Filter":"All","Criteria":[{"criteriaName":"Criteria_1",
 "Conditions":[{"variableName":"STITags_SalesTransactionActionType","operator":"Equals",
 "valueDataType":"string","value":"Add","valueType":"Literal","sequenceNumber":"1"}],
 "ConditionLogic":"1","SequenceNumber":"1"}],
 "Variables":[{"collection":true,"name":"STITags_SalesTransactionActionType","dataType":"string",
 "type":"Tag","fieldType":"INPUT,OUTPUT","contextTag":"SalesTransactionActionType","category":"STITags"}]}]}
```

- In the UI, a decomposition-rule condition is on the source product's Decomposition tab: the
  connector to the technical product > Execution Rules, Based On Sales Transaction Items.
- A step condition is on the workspace's step > Configure Execution Rules. Skip Branch is a
  toggle on the rule list after saving, and writes `IsSkipBranch`.
- By API, a REST PATCH of `ConditionData` (decomposition rule) or `ExecuteOnConditionData`
  (step definition) set `ExecuteOnRuleId` to a new generated RuleSet, as the UI did. A null
  `ExecuteOnRuleId` after a write means the condition didn't save.
- Use the context tag name, not the attribute name: `LineItemQuantity`, `ItemStartQuantity`,
  `ItemEndQuantity`, `SalesTransactionActionType`, `ItemSalesTransactionAction`.
  `Quantity` was refused: "a valid value in ContextTag field should be provided".
- Numbers take `dataType` and `valueDataType` `number`; `double` and `decimal` were refused
  with "No enum constant …RuleRefVariableDataType".
- Other validator messages seen: "Specify a value for Rules" and "The JSON structure is invalid".
- These tags evaluated correctly in decomposition-rule conditions, but False in step
  conditions on a new sale; see **Lifecycle orders** in
  [updates-and-runtime.md](updates-and-runtime.md). The standard context's rule library was
  enough for these tags.

## 4. Deploy in Dependency Order

Use [CSV/SFDMU](csv-and-sfdmu.md) for normal configuration records. Deploy setup and
metadata dependencies through their supported surfaces before their data references.

1. Confirm DRO settings/permissions and selected active contexts; align rule library.
2. Ensure catalog, classifications, attributes/picklist values, expression sets,
   flows, providers and required credential access exist. Apply only requested changes.
3. Create custom scopes if used, after their context tags/mappings exist. Use a
   reviewed JSON file and the existing task rather than a data-object CSV:

   ```bash
   cci task run manage_fulfillment_scope_cnfg --org "$CCI_ORG" \
     -o operation upsert -o input_file "your-scope-file.json" -o dry_run true
   cci task run manage_fulfillment_scope_cnfg --org "$CCI_ORG" \
     -o operation upsert -o input_file "your-scope-file.json"
   ```

   Leave invalid-tag handling at its fail default. A required scope being skipped
   is not a successful deployment; report and correct its context prerequisite.
4. Load decomposition rules, transform groups/transforms, enrichment rules and
   variable mappings as needed. Load all step groups before steps, steps before
   dependencies; then scenarios and workspace membership. Providers/queues must
   precede fallout, jeopardy and assignment rules.
5. Refresh decision tables used by fallout/jeopardy after their source rules change.
   Discover tables by source object and inspect related sources/criteria using
   [decision-tables](../decision-tables/SKILL.md). The two DRO tables exist only after the
   Setup toggle in the settings checklist; expect `FulfillmentFalloutRules` and
   `Fulfillment_Step_Jeopardy_Rule_Decision_Table`, both Active [Measured: 2026-11-16, 264,
   scratch, one org]:

   ```bash
   sf data query --target-org "$SF_ORG" --query "SELECT DeveloperName, Status, LastSyncDate FROM DecisionTable WHERE SourceObject IN ('FulfillmentFalloutRule','FulfillmentStepJeopardyRule')"
   ```

   For each relevant table, refresh, then confirm `LastSyncDate` moved:

   ```bash
   python scripts/decision_tables/refresh_decision_table.py \
     --target-org "$SF_ORG" --developer-name "your-table-api-name"
   python scripts/decision_tables/refresh_decision_table.py \
     --target-org "$SF_ORG" --developer-name "your-table-api-name" --confirm
   ```

   Refresh queues asynchronous work; confirm completion and resulting data through
   the owning workflow. A queued job or unrelated pricing refresh proves nothing
   about DRO rules. Technical products must be active when used at runtime;
   design records do not share a universal activate-all step.

## 5. Verify Configuration and Runtime Separately

Read back all intended records/values, relationship IDs, condition fields and
generated references. Account for loader errors, missing rows, and explicit clears.
For a new dataset, repeat loading in a disposable org and compare identities and
values as well as counts. Do not retry an uncertain write before checking state.

For an authorized test order, use the existing submission flow or documented
Submit Sales Transaction action. Define expected outputs before submission and
inspect the fulfillment request until composition succeeds or fails. Verify
decomposed products/quantities/attributes, chosen scenarios, step multiplicity,
definition IDs, predecessor edges, scope pairing, and true/false condition cases.
Exercise custom scopes, compensation and advanced rules when included in the change.

Do not start a test order with external side effects unless that test is authorized.
Bound waits by a stated test timeout and stop on rejection/fatal failure. Report
request/plan IDs, actual versus expected evidence, outstanding manual tasks or
credentials, and whether fulfillment completed. Record no runtime verification
when only offline/simulation checks ran.
