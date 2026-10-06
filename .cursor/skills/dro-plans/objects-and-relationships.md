# DRO Objects and Relationships

Use this graph to choose configuration, not as a mandate to populate every
object. Schema sources are the [DRO domain](../revenue-cloud-data-model/domains/dro.md),
[ERD](../../../docs/erds/erd-data.json), and
[264 describe capture](../../../scripts/erd/schema_diff/264-schema.json).
Use target describes to confirm writeability, required fields, lookup targets,
picklists, and autonumber behavior. Capture fields are keyed by field name.

## Decomposition and Enrichment

| Object | Exact relationship fields → target | Identity and use |
| --- | --- | --- |
| `Product2` | Catalog/classification/attribute wiring comes from the PCM model | Verified unique SKU or external key; configure `DecompositionScope`, `CustomDecompositionScope`, `FulfillmentQtyCalcMethod` only on intended products |
| `ProductFulfillmentDecompRule` | `SourceProductId`, `DestinationProductId` → `Product2`; `SourceProductClassificationId` → `ProductClassification`; `ExecuteOnRuleId` → `Ruleset` | Unique chosen Name; source product or classification → destination technical product; `Priority` and `ConditionData` affect selection |
| `ValTfrmGrp` | None required by this graph | Unique chosen Name; primitive types/enumeration configuration for value transformation |
| `ValTfrm` | `ValueTransformGroupId` → `ValTfrmGrp`; `InputPicklistValueId`, `OutputPicklistValueId` → `AttributePicklistValue` | Name can be autonumber; derive identity from group plus typed input, checking uniqueness |
| `ProductDecompEnrichmentRule` | `DecompositionRuleId` → `ProductFulfillmentDecompRule`; `SourceAttributeDefinitionId`, `DestinationAttributeDefinitionId` → `AttributeDefinition`; `ListMappingGroupId` → `ValTfrmGrp`; `CalculationDefinitionId` → `DecisionMatrixDefinition` or `ExpressionSet` | Name is autonumber; match a verified unique combination of rule, source/destination types and identifiers; use target-supported writable fields |
| `ProdtDecompEnrchVarMap` | `ProductDecompEnrichmentRuleId` → `ProductDecompEnrichmentRule`; `AttributeDefinitionId` → `AttributeDefinition` | Inspect variable fields to build a unique rule/variable identity; optional calculation input mapping |

Enrichment uses `SourceType`, `DestinationType`, `SourceApiName`,
`DestinationApiName`, context tags, and attribute identifiers as appropriate.
`CalculationMethod` selects direct copy, list mapping, or expression calculation;
use API values from the target. Do not substitute UI labels for API values.
Inspect technical-bundle catalog relationships separately when decomposition
targets a bundle; a decomposition rule is not a bundle-component definition.

## Orchestration Configuration

| Object | Exact relationship fields → target | Identity and use |
| --- | --- | --- |
| `FulfillmentStepDefinitionGroup` | No parent lookup required | Unique chosen Name; target-supported fulfillment `UsageType` |
| `FulfillmentStepDefinition` | `StepDefinitionGroupId`, `AmendGroupId`, `CancelledGroupId` → `FulfillmentStepDefinitionGroup`; `AssignedToId` → `User` or `Group`; `RunAsUserId` → `User`; `IntegrationDefinitionNameId` → `IntegrationProviderDef`; `ExecuteOnRuleId`, `ResumeOnRuleId` → `ExpressionSet` or `Ruleset` in the captured schema | Unique chosen Name or verified group/Name key; group membership, type, scope, conditions, execution schedule, compensation |
| `FulfillmentStepDependencyDef` | `FulfillmentStepDefinitionId`, `DependsOnStepDefinitionId` → `FulfillmentStepDefinition` | Unique Name or verified edge key; **dependent step** is the first field, **predecessor** the second; includes `DependencyScope`, `CustomScope`, propagation/reverse compensation |
| `ProductFulfillmentScenario` | `ProductId` → `Product2`; `ProductClassificationId` → `ProductClassification`; `FulfillmentStepDefnGroupId` → `FulfillmentStepDefinitionGroup`; `ScenarioRuleId` → `Ruleset`; `FulfillmentProcessId` → `FlowOrchestration` or `FlowRecord` in the captured schema | Unique chosen Name; product/classification/order eligibility and actions; `ConditionData`; ordinary step-group scenarios need no process lookup |
| `FulfillmentWorkspace` | None | Unique chosen Name; authoring/viewer container |
| `FulfillmentWorkspaceItem` | `FulfillmentWorkspaceId` → `FulfillmentWorkspace`; `FulfillmentStepDefinitionGroupId` → `FulfillmentStepDefinitionGroup` | Autonumber Name; match workspace/group pair, maintain `ShowOrder` |
| `FulfillmentFalloutRule` | `FalloutQueueId` → `Group`; `IntegrationDefinitionId` → `IntegrationProviderDef` | Autonumber Name in repository analysis; derive unique type/provider-or-flow/error criteria; retries and routing |
| `FulfillmentStepJeopardyRule` | `IntegrationDefinitionId` → `IntegrationProviderDef` | Autonumber Name in repository analysis; derive unique type/provider-or-flow criteria; duration and jeopardy thresholds |
| `FulfillmentTaskAssignmentRule` | `SourceId` → `Group`; `DestinationId` → `Group` or `User`; `ConditionId` → `ExpressionSet` or `Ruleset` | Unique chosen Name; queue/source, destination, priority, allocation and `ConditionData` |

An `idLookup` field is not evidence that its values are unique. Query both source
and target before selecting a matching key. Names are convenient only when
convention-unique across the records the loader can match. For autonumber objects,
prove a semantic composite identifies one row; if no safe key exists, use a
targeted ID-based update after discovery rather than claiming portable Upsert.

## Setup and External Dependencies

| Dependency | Relationship/check | Route |
| --- | --- | --- |
| `CustomFulfillmentScopeCnfg` | `DeveloperName` referenced by `Product2.CustomDecompositionScope`, step `CustomFulfillmentScope`, dependency `CustomScope`; `ItemContextTag` resolves to String | Tooling API; existing `manage_fulfillment_scope_cnfg` task; not an ordinary SFDMU data object |
| DRO settings/context mappings | Selected active context, sales/fulfillment nodes, attributes/tags, asset context if used | Setup/Metadata/Tooling as supported by target; `OrchestrationPlanCtxMapping` has documented Metadata/Tooling surfaces |
| Context rule library | Active `UsageType=Dfo` library/version linked to the selected sales context | Discover library hierarchy; preserve latest rule sets when versioning; do not blindly invoke the repository seed |
| `IntegrationProviderDef` | `DeveloperName` referenced through each object's distinct provider relationship | Repository metadata uses the `IntegrationProviderDef` XML root in `integrationProviderDefinitions/`; confirm target deployment support and deploy providers/flows before references, with credential access required for successful execution |
| Users and queues | Resolve polymorphic target type; users active, queue membership/object eligibility correct | ReadOnly lookup records; assignee, execution user and fulfillment user have different purposes |
| Attributes/picklist values | Attribute codes and picklist names agree across orgs | Catalog prerequisites before conditions and transformations |
| Expression sets/decision matrices | Calculation or explicit expression lookup available and activated as required | Owning skills; target-supported polymorphic matching |
| Fallout/jeopardy decision tables | Relevant tables exist and materialized data includes new rules | Discover, refresh and verify via decision-table tools |

## Runtime Evidence — Do Not Seed as Configuration

| Runtime record | Relationship used for inspection |
| --- | --- |
| `SalesTransactionFulfillReq` | `ReferenceObjectId` → transaction; `PlanId` → `FulfillmentPlan`; `PreviousRequestId` → prior request |
| `FulfillmentOrder` / `FulfillmentOrderLineItem` | Inspect order linkage on target; line `FulfillmentOrderId`, `OrderItemId`, `Product2Id`, `FulfillmentAssetId` track decomposition |
| `FulfillmentLineSourceRel` | `FulfilmentOrderLineId` → generated `FulfillmentOrderLineItem`; `SourceLineItemId` → `OrderItem` or another `FulfillmentOrderLineItem`; inspect this relationship to establish decomposition lineage |
| `FulfillmentStep` | `FulfillmentPlanId`, `FulfillmentStepDefinitionId` link runtime step to plan/template |
| `FulfillmentStepDependency` | `FulfillmentStepId`, `DependsOnStepId`, `DependencyDefinitionId` link instantiated dependent/predecessor and definition |
| `FulfillmentStepSource` | `StepId` → step; `SourceLineItemId` → source, including `OrderItem`/`FulfillmentOrderLineItem` |
| `FulfillmentAsset` and attribute/relationship/state records | Inspect target schema for assetization and lineage |
| `AssetFulfillmentDecomp` | `FulfillmentSourceAssetId`, `FulfillmentTargetAssetId` track decomposed asset linkage |

Correlate by transaction/request/plan and actual definition IDs, not record Names
alone. Step scope determines multiplicity; dependency scope determines which
predecessor instances each dependent waits for. Workspace membership controls
authoring visibility; scenarios control inclusion during plan composition.
