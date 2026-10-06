# DRO CSV Authoring and SFDMU Loading

Read the [SFDMU data-plan skill](../sfdmu-data-plans/SKILL.md) first; it owns v5
syntax, operation safety, empty-file behavior and extraction edge cases. This
reference adds DRO-specific selection and a minimal worked dataset.

## Dataset Contract

Use `datasets/sfdmu/<family>/<locale>/<plan>/` for tracked datasets, following the
nearest catalog family. Include `export.json`, a CSV per file-backed writable object,
and a README describing prerequisites, operations, matching keys, counts, load
sequence, verification and known limits. A plan contains configuration, not
runtime orders/plans/steps. Do not put a temporary target-org delta in tracked
source unless it represents intended fresh-build configuration.

ReadOnly references resolve from the target and do not generally require a source
CSV; the SFDMU skill documents live evidence for that behavior. Keep illustrative
lookup CSVs only when useful or needed by the selected supported loader mechanism.
Do not create empty reference files merely to satisfy a checker. Match CSV filename
case exactly to the query's FROM object, including per-pass overrides.

Choose keys by querying source and target uniqueness. Namespace chosen Names
when matching by Name so independent plans cannot accidentally update each other.
Use Upsert for configuration, Update for existing product settings, ReadOnly for
external lookup records. New technical products belong to an upstream PCM plan
or an explicitly scoped catalog creation change. Never copy full catalog rows
just to include a single product lookup.

| Relationship CSV header | Lookup ID field |
| --- | --- |
| `SourceProduct.StockKeepingUnit`, `DestinationProduct.StockKeepingUnit` | `ProductFulfillmentDecompRule.SourceProductId`, `.DestinationProductId` |
| `SourceProductClassification.Name` | Decomposition `.SourceProductClassificationId` |
| `StepDefinitionGroup.Name` | Step `.StepDefinitionGroupId` |
| `AmendGroup.Name`, `CancelledGroup.Name` | Step `.AmendGroupId`, `.CancelledGroupId` |
| `IntegrationDefinitionName.DeveloperName` | Step `.IntegrationDefinitionNameId` |
| `FulfillmentStepDefinition.Name`, `DependsOnStepDefinition.Name` | Dependency's dependent and predecessor IDs |
| `FulfillmentStepDefnGroup.Name` | Scenario `.FulfillmentStepDefnGroupId` |
| `Product.StockKeepingUnit`, `ProductClassification.Name` | Scenario `.ProductId`, `.ProductClassificationId` |
| `FulfillmentWorkspace.Name`, `FulfillmentStepDefinitionGroup.Name` | Workspace-item parent IDs |
| `DecompositionRule.Name`, `ListMappingGroup.Name` | Enrichment `.DecompositionRuleId`, `.ListMappingGroupId` |
| `ValueTransformGroup.Name` | Transform `.ValueTransformGroupId` |
| `IntegrationDefinition.DeveloperName` | Fallout/jeopardy `.IntegrationDefinitionId` |

Confirm each relationship name in target describe and ensure reference objects
are available to SFDMU. Query ID fields in `export.json`; portable CSVs use their
relationship headers. Traversal fields used in external IDs must also be queried.
Do not use a `$$` parent composite as a child lookup reference. If a simple parent
key cannot be made unique, use another verified single-field key or a targeted
API operation instead of guessing which parent SFDMU will choose.

## Worked Minimal Dataset — Not Live-Verified

This example targets an **already existing, active technical product** whose
unique SKU is `EXAMPLE-DRO-TECH`. Replace that SKU and the `Example DRO` Names
with your chosen keys. It configures two LineItem milestones and their dependency,
an Add scenario, a group and a workspace. Milestones avoid assigning a fabricated
user or invoking an external system. Operator completion is needed to test their
execution; this example does not implement provisioning.

The API/picklist values below match the captured 264 schema; verify them in the
target. Direct fulfillment needs no source→technical decomposition rule here.
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

The workspace item uses a portable composite matching column; its two **lookup**
columns remain simple references. `deleteOldData` is intentionally absent.
The semicolon is the matching-key value delimiter; commas delimit CSV columns.
Quote cells containing commas/newlines/quotes using standard CSV escaping.

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
ReadOnly references do not generally need source CSVs. For user assignment, use
`AssignedToId$User` in typed query syntax and `AssignedTo.Name` in the CSV.

An explicit assignee, execution user, or queue needs its own verified target
mapping. User Names need not be unique; choose another supported unique key when
necessary. A queue is `Group` with `Type='Queue'`, not a separate data SObject.
Validate membership and eligibility. Polymorphic fields require typed SFDMU query
notation (the shipped user example uses `AssignedToId$User`); follow the SFDMU
polymorphic guidance and simulation before mixing User/Group destinations.
Default-user replacement is not a general queue/RunAsUser remapping mechanism.

## Validate, Simulate and Load

Use shell variables with concrete values, from the repository root:

```bash
DRO_PLAN="datasets/sfdmu/your-family/en-US/your-dro-plan"
CCI_ORG="your-cci-alias"
SF_ORG="your-sf-alias-or-username"
python scripts/ai/generate_plan_readme.py "$DRO_PLAN"
python scripts/ai/check_plan_readme_consistency.py --strict "$DRO_PLAN"
python scripts/validate_sfdmu_v5_datasets.py
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

Require zero Critical/High validator findings and zero strict README errors/warnings.
Inspect simulation and live logs, row-error/missing-reference files, per-object
counts and target read-back. If a record failed, fix its cause before dependent
records; do not treat a successful process exit as sufficient.

Use diagnostics generated by the **current run**, not stale `source/`, `target/`
or report files inherited from earlier loads/extracts. Inspect target CSV `Errors`
where present and reconcile final records against expected values. A missing-parent
report from an early pass may be transient: verify the final lookup IDs before
declaring permanent failure. Conversely, unresolved references or actual target-row
errors remain failures even when the process exits zero. Preserve current failure
reports before temporary files are removed; do not assume automatic archival in
this checkout's CCI loader.

In a disposable org, record IDs/keys/values after the first load and repeat the
same load. Require stable identities/counts and intended field values, with no
delete/reinsert churn. The existing `test_qb_dro_idempotency` can be overridden
with `pathtoexportjson`, but its documented default-user limitation applies;
two explicit loader runs plus read-back cover dynamic assignment. Follow
[updates-and-runtime.md](updates-and-runtime.md) for used orgs and null clears.

## Extract Existing Configuration

Use a reviewed export plan that includes all fields needed for the intended
round trip; the shipped plan omits some condition/advanced fields.

```bash
cci task run extract_qb_dro_data --org "$CCI_ORG" \
  -o pathtoexportjson "$DRO_PLAN" -o output_dir "/tmp/dro-extraction" \
  -o referenceplandir none -o run_post_process true
```

Explicit output prevents writing extraction results over authored CSVs;
`referenceplandir none` prevents automatic alignment to the QB schema from
dropping a custom dataset's fields. Review `processed/` output, composite
matching columns, normalized relationship headers, condition JSON, missing
references and portable identities. Extract custom scopes separately with the
scope task and retrieve required metadata through supported surfaces. No data
extract is a complete backup of settings, secrets or external-system effects.
