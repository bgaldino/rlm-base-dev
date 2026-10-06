# Authoring and Deploying DRO Configuration

## 1. Resolve the Target and Existing State

Use an explicit target for every operation. CCI and SF CLI have different alias
registries: resolve both to the same username/org ID before loading. Do not print
access tokens; CLI commands take aliases/usernames, never tokens. Read
[CCI orchestration](../cci-orchestration/SKILL.md) for registry/task mechanics.

In a Git worktree, CCI may fail project discovery because `.git` is a file.
The installed runtime supports environment overrides: set
`CUMULUSCI_AUTO_DETECT=1`, `CUMULUSCI_REPO_ROOT` to this checkout's absolute root,
`CUMULUSCI_REPO_URL` to its verified origin URL, and `CUMULUSCI_REPO_BRANCH` to
its current feature branch. Use `CUMULUSCI_REPO_COMMIT` if an operation needs
the current commit. These select the actual checkout; do not replace its Git
metadata or point at another checkout just to make a command resolve.

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
  `ManualTask` needs suitable assignment and no callout provider. `Milestone`,
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
- **Optional features:** delays/custom dates, branch skipping, cross-plan
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
different records. A decomposition rule maps a commercial product to a technical
`Product2`; submission generates `FulfillmentOrderLineItem` records and source
relationships. A fulfillment scenario alone can select steps without generating
technical outputs. Do not insert runtime lines to fill an empty UI panel.

1. Specify the technical outcomes, such as Project Service and Billing Setup,
   and expected lines per source line. Reuse suitable technical products; create
   new ones through an upstream catalog dataset or explicitly scoped creation.
   Keep their pricing/usage significance separate from the commercial product.
2. Confirm destinations are active. Choose assetizability, decomposition scope,
   and quantity behavior deliberately. `OrderLineItem` with `AlwaysOne` is a
   useful service example: one technical item of quantity one per source line,
   even if the commercial line's quantity is ten. `Aggregate` serves a different
   quantity requirement. Product decomposition scope controls technical-item
   grouping; step `Scope` controls step multiplicity.
3. Create `ProductFulfillmentDecompRule` records using verified source and
   destination SKUs, unique names, and priorities. One source can have two rules
   for two distinct technical outcomes. Check inherited classification rules,
   conditions, destination overlaps, and cycles before adding another rule.
4. Decide where scenarios apply. To orchestrate the decomposed item, bind the
   intended group to the technical destination. When moving an existing direct
   scenario, update its discovered ID and preserve its identity. Review other
   source/classification/destination scenarios so the same project work is not
   selected twice. Separate commercial-level work can remain when intentional.
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

On an authorized fresh test order, verify generated product IDs, quantities,
source relationships, steps, and edges—not just counts. Configuration changes
do not retrofit a submitted plan. Respect a user's choice to test manually and
report runtime generation as unverified until evidence is available. See the
[CSV extension](csv-and-sfdmu.md#worked-decomposition-extension) and
[technical-product sources](examples-and-grounding.md#authoritative-article-map).

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
   [decision-tables](../decision-tables/SKILL.md). For each relevant table:

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
