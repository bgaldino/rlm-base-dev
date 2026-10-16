# DRO CSV Authoring and SFDMU Loading

This reference covers DRO object selection, relationship headers, loader routing,
and a worked dataset. The [SFDMU data-plan skill](../sfdmu-data-plans/SKILL.md)
owns general plan syntax, operation safety, CSV conventions, extraction behavior,
and validation. Follow it for those mechanics instead of duplicating its rules here.

## Dataset Contract

Place reusable datasets under
`datasets/sfdmu/<family>/<locale>/<plan>/`, following the nearest catalog family.
They describe configuration, not runtime orders, plans, or steps. Keep a plan
narrow to its intended configuration graph; a technical product belongs in an
upstream PCM plan unless its creation is explicitly in scope. Follow the SFDMU
skill and `AGENTS.md` for file layout, README, key-selection, and operation rules.

Use the [CSV relationship-header map](objects-and-relationships.md#csv-relationship-headers)
for DRO lookups. Confirm fields and `referenceTo` values with target describes;
query the lookup ID and relationship traversal needed by the plan. A relationship
header is for resolving a parent, not a substitute for selecting a safe matching
key. If no portable unique parent key exists, use a targeted API operation.

## Worked Minimal Dataset — Not Live-Verified

This example targets an **already existing, active technical product** whose
unique SKU is `EXAMPLE-DRO-TECH`. Replace that SKU and the `Example DRO` Names
with your chosen keys. It configures two LineItem milestones and their dependency,
an Add scenario, a group and a workspace. Milestones avoid assigning a fabricated
user or invoking an external system. Operator completion is needed to test their
execution; this example does not implement provisioning.

The API/picklist values below illustrate the repository schema snapshot; verify
them against the target release and org. Direct fulfillment needs no
source→technical decomposition rule here.
If the order sells another commercial product, add the actual decomposition
rule and test its outputs before relying on this technical-product scenario.

`export.json`:

```json
{
  "apiVersion": "68.0",
  "excludeIdsFromCSVFiles": "true",
  "objects": [
    {
      "query": "SELECT Id, StockKeepingUnit FROM Product2",
      "operation": "ReadOnly",
      "externalId": "StockKeepingUnit"
    },
    {
      "query": "SELECT Id, Name, UsageType FROM FulfillmentStepDefinitionGroup",
      "operation": "Upsert",
      "externalId": "Name"
    },
    {
      "query": "SELECT Id, Name, StepDefinitionGroupId, StepType, Scope, UsageType FROM FulfillmentStepDefinition",
      "operation": "Upsert",
      "externalId": "Name"
    },
    {
      "query": "SELECT Id, Name, FulfillmentStepDefinitionId, DependsOnStepDefinitionId, DependencyScope FROM FulfillmentStepDependencyDef",
      "operation": "Upsert",
      "externalId": "Name"
    },
    {
      "query": "SELECT Id, Name, ProductId, FulfillmentStepDefnGroupId, Action, UsageType FROM ProductFulfillmentScenario",
      "operation": "Upsert",
      "externalId": "Name"
    },
    {
      "query": "SELECT Id, Name, Description FROM FulfillmentWorkspace",
      "operation": "Upsert",
      "externalId": "Name"
    },
    {
      "query": "SELECT Id, FulfillmentWorkspaceId, FulfillmentStepDefinitionGroupId, FulfillmentWorkspace.Name, FulfillmentStepDefinitionGroup.Name, ShowOrder FROM FulfillmentWorkspaceItem",
      "operation": "Upsert",
      "externalId": "FulfillmentWorkspace.Name;FulfillmentStepDefinitionGroup.Name"
    }
  ]
}
```

`Product2.csv` (reference only):

This file illustrates the SKU prerequisite; the ReadOnly declaration can resolve
the existing product without it. The SKU must still identify the scenario's target.

```csv
StockKeepingUnit
EXAMPLE-DRO-TECH
```

`FulfillmentStepDefinitionGroup.csv`:

```csv
Name,UsageType
Example DRO Delivery,Fulfillment
```

`FulfillmentStepDefinition.csv`:

```csv
Name,StepDefinitionGroup.Name,StepType,Scope,UsageType
Example DRO Ready,Example DRO Delivery,Milestone,LineItem,Fulfillment
Example DRO Delivered,Example DRO Delivery,Milestone,LineItem,Fulfillment
```

`FulfillmentStepDependencyDef.csv`:

```csv
Name,FulfillmentStepDefinition.Name,DependsOnStepDefinition.Name,DependencyScope
Example DRO Ready Before Delivered,Example DRO Delivered,Example DRO Ready,LineItem
```

`ProductFulfillmentScenario.csv`:

```csv
Name,Product.StockKeepingUnit,FulfillmentStepDefnGroup.Name,Action,UsageType
Example DRO Delivery On Add,EXAMPLE-DRO-TECH,Example DRO Delivery,Add,Fulfillment
```

`FulfillmentWorkspace.csv`:

```csv
Name,Description
Example DRO Workspace,Example technical product delivery
```

`FulfillmentWorkspaceItem.csv`:

```csv
FulfillmentWorkspace.Name,FulfillmentStepDefinitionGroup.Name,ShowOrder,$$FulfillmentWorkspace.Name$FulfillmentStepDefinitionGroup.Name
Example DRO Workspace,Example DRO Delivery,1,Example DRO Workspace;Example DRO Delivery
```

The workspace item's `$$` column is its matching key; its parent lookup columns
are ordinary single-field references. Follow the SFDMU skill for delimiter,
escaping, empty-file, and destructive-operation rules.

For two eligible order lines, expect four steps: Ready and Delivered for each
line, with each Delivered depending on its corresponding Ready. Verify actual
source linkage and edges; counts alone could conceal incorrect scope pairing.

## Worked Decomposition Extension

Extend the minimal example above when an existing commercial product
`EXAMPLE-COMM-SERVICE` must produce the technical `EXAMPLE-DRO-TECH` item.
Replace these illustrative keys with unique target identities. The existing
scenario remains on the **technical** SKU, not a second copy on the commercial
SKU. The commercial product's pricing and usage settings remain outside this
fulfillment dataset.

If the technical product already exists, retain Product2 as ReadOnly and add
the decomposition-rule declaration after it, before scenarios. If creating the
technical product is explicitly in scope, use two `objectSets`:

- Pass 1: only the Product2 Upsert declaration below, backed by Product2.csv.
- Pass 2: the existing minimal example's objects, with Product2 ReadOnly resolving
  both source and destination SKUs and the rule declaration immediately after it.
  Keep the existing group/step/dependency/scenario/workspace declarations.

Replace the top-level `objects` array with these passes; do not leave it populated
alongside `objectSets`. The same Product2 CSV serves the creation pass; the
ReadOnly pass resolves target records without requiring commercial source rows.

Pass 1 Product2 declaration:

```json
{
  "query": "SELECT Id, Name, StockKeepingUnit, ProductCode, IsActive, IsAssetizable, DecompositionScope, FulfillmentQtyCalcMethod FROM Product2 WHERE StockKeepingUnit = 'EXAMPLE-DRO-TECH'",
  "operation": "Upsert",
  "externalId": "StockKeepingUnit"
}
```

Replace the minimal example's optional reference-only Product2.csv with:

```csv
Name,StockKeepingUnit,ProductCode,IsActive,IsAssetizable,DecompositionScope,FulfillmentQtyCalcMethod
Example Project Service,EXAMPLE-DRO-TECH,EXAMPLE-DRO-TECH,true,false,OrderLineItem,AlwaysOne
```

Verify required fields against target describe; include any required catalog
fields before creation. Non-assetizable, unpriced technical products are this
example's choice, not a requirement for every technical catalog.

In pass 2, restrict the Product2 ReadOnly query to the two SKUs. Add this rule:

```json
{
  "query": "SELECT Id, Name, SourceProductId, DestinationProductId, SourceProduct.StockKeepingUnit, DestinationProduct.StockKeepingUnit, Priority FROM ProductFulfillmentDecompRule",
  "operation": "Upsert",
  "externalId": "Name"
}
```

ProductFulfillmentDecompRule.csv:

```csv
Name,SourceProduct.StockKeepingUnit,DestinationProduct.StockKeepingUnit,Priority
Example Service To Project,EXAMPLE-COMM-SERVICE,EXAMPLE-DRO-TECH,10
```

For one eligible commercial line of quantity ten, expect one technical line of
quantity one, its source relationship, and the example's two dependent steps.
Two separate source lines should produce two technical lines and four steps.
To model two outputs per source line, add a second technical destination and
rule, plus its intended scenario/group; verify grouping and any dependencies
between the outputs. Do not duplicate the original group's work unintentionally.
Inspect generated records only after an authorized submission; offline validation
of these fragments does not prove runtime decomposition.

## Adding Decomposition, Conditions and Other Features

- Add intended Product2 Update columns only when changing decomposition settings;
  retain portable product keys and include catalog prerequisites.
- Add `ProductFulfillmentDecompRule` before enrichment children, with source
  product/classification and destination keys, chosen Name and Priority.
- Add transforms and required attribute/picklist references before enrichment and
  variable mappings. Avoid autonumber Name matching; prove composite uniqueness.
- Add target-supported condition JSON fields to SELECT and CSV together. Use
  correctly CSV-escaped, verified JSON; remap attribute codes/resources across
  orgs. Do not copy generated RuleSet IDs from the source org.
- Add provider ReadOnly lookups and the correct per-object relationship fields
  for callout/fallout/jeopardy rules. Add Flow fields for AutoTask steps.
- Add only populated optional CSVs. If retaining an empty placeholder, mark that
  object `excluded: true`; absence of rows is not an instruction to delete.

## User/Queue Portability

For default user assignment, the existing loader supports
`dynamic_assigned_to_user: true`: `AssignedTo.Name` contains
`__DRO_ASSIGNED_TO_USER__`, with `User.csv` and the supporting `UserAndGroup.csv`
using the same placeholder. Follow the shipped `qb-dro` schema for this mode;
the loader substitutes the target org user's Name in a temporary copy.
Verify uniqueness of that Name in the target, not only the resolved username.
ReadOnly references do not generally need source CSVs. For this user lookup, the
query uses `AssignedToId$User` and the CSV uses `AssignedTo.Name`.

An explicit assignee, execution user, or queue needs its own verified target
mapping. User Names need not be unique; choose another supported unique key when
necessary. A queue is `Group` with `Type='Queue'`, not a separate data SObject.
Validate membership and eligibility. For mixed User/Group destinations, follow
the SFDMU polymorphic-field guidance and simulate before loading.
Default-user replacement is not a general queue/RunAsUser remapping mechanism.

## Validate, Simulate and Load

Use shell variables with concrete values, from the repository root:

```bash
DRO_PLAN="datasets/sfdmu/your-family/en-US/your-dro-plan"
CCI_ORG="your-cci-alias"
SF_ORG="your-sf-alias-or-username"
cci task run insert_qb_dro_data --org "$CCI_ORG" \
  -o pathtoexportjson "$DRO_PLAN" -o targetusername "$SF_ORG" \
  -o dynamic_assigned_to_user "" -o simulation true
```

Despite the task's QB name, the `pathtoexportjson` override loads
the selected plan using `LoadSFDMUData`. Verify the CCI and SF targets identify the
same org. Explicit `targetusername` avoids the loader's connected-org fallback
to an access token. The loader uses Python truthiness for these options:
CLI `false` is a nonempty string, so it does **not** disable either option. Pass
an empty string to disable dynamic assignment (overriding the task's true default)
or simulation; pass `true` to enable them. Turn dynamic assignment on only when
the dataset uses its placeholder. **The next command writes to the org**; run
only for an authorized target after preflight/prerequisites:

```bash
cci task run insert_qb_dro_data --org "$CCI_ORG" \
  -o pathtoexportjson "$DRO_PLAN" -o targetusername "$SF_ORG" \
  -o dynamic_assigned_to_user "" -o simulation ""
```

If the target is authenticated only in the SF CLI and has no CCI alias, direct
`sf sfdmu run` can be used for a dataset that needs no CCI-side preprocessing.
Use the same reviewed plan path and SF alias for simulation and load; do not pass
or log access tokens. Resolve any SFDMU production-style host confirmation by
verifying the target identity first. This fallback does not perform the CCI
loader's dynamic assignee substitution or other task-side processing.

Run the shared validators and README checks described in the SFDMU skill and
`AGENTS.md`. The DRO-specific acceptance check is target read-back of the intended
configuration and relationships after loading; simulation is only a preflight.

When the test order is created with the Transaction Data Harness, run its `plan`
command before creating records. If a product has multiple active PricebookEntry
selling models, pin the intended `selling_model` in the scenario YAML; the harness
cannot choose safely from several valid models. Inspect the resolved product,
pricebook, account and target stage before continuing.

If SFDMU classifies the target host as production and requests `--canmodify`,
verify the authenticated org identity and authorization first; simulation does
not bypass this identity guard. For idempotency, use a disposable org and verify
stable record identities and intended relationships after two loads. The existing
`test_qb_dro_idempotency` can be overridden with `pathtoexportjson`, but its
documented default-user limitation applies; two explicit loader runs plus read-back
cover dynamic assignment. Follow
[updates-and-runtime.md](updates-and-runtime.md) for used orgs and null clears.

## Extract Existing Configuration

Use the [SFDMU extraction guidance](../sfdmu-data-plans/SKILL.md) for a reviewed
export plan and generic post-processing. For DRO, include condition/advanced
fields omitted by the shipped plan and preserve custom fields during processing.

```bash
cci task run extract_qb_dro_data --org "$CCI_ORG" \
  -o pathtoexportjson "$DRO_PLAN" -o output_dir "/tmp/dro-extraction" \
  -o referenceplandir none -o run_post_process true
```

Use a separate output directory and `referenceplandir none` so the QB schema does
not drop custom fields. Review normalized DRO relationship headers, condition JSON,
and portable identities. Extract custom scopes separately and retrieve required
metadata through supported surfaces; data extraction does not capture settings,
secrets, or external-system effects.
