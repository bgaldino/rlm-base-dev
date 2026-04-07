# DRO — Dynamic Revenue Orchestration

27 objects managing fulfillment plans, step definitions, decomposition rules, and orchestration workflows.

## Design-Time Objects (Configuration)

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `FulfillmentStepDefinitionGroup` | Groups step definitions | Name |
| `FulfillmentStepDefinition` | Template for a fulfillment step | Name, AssignedToId (polymorphic: User/Group), StepDefinitionGroupId, IntegrationDefinitionNameId |
| `FulfillmentStepDependencyDef` | Dependency between step definitions | FulfillmentStepDefinitionId, DependsOnStepDefinitionId |
| `ProductFulfillmentDecompRule` | Decomposition rule: source product → destination product | Name, SourceProductId, DestinationProductId, SourceProductClassificationId |
| `ProductDecompEnrichmentRule` | Enrichment during decomposition | DecompositionRuleId, SourceAttributeDefinitionId, DestinationAttributeDefinitionId |
| `ProductFulfillmentScenario` | Links product/classification to a step group | ProductId, ProductClassificationId, FulfillmentStepDefnGroupId |
| `FulfillmentFalloutRule` | Handles step failures | FalloutQueueId (→ Group), IntegrationDefinitionId |
| `FulfillmentStepJeopardyRule` | Time-based escalation rules | IntegrationDefinition.DeveloperName |
| `FulfillmentTaskAssignmentRule` | Dynamic task assignment rules | ConditionId, DestinationId, SourceId (polymorphic) |
| `FulfillmentWorkspace` | Workspace UI grouping | Name |
| `FulfillmentWorkspaceItem` | Junction: Workspace ↔ StepDefinitionGroup | FulfillmentWorkspaceId, FulfillmentStepDefinitionGroupId |
| `ValTfrmGrp` | Value transformation groups | Name |
| `ValTfrm` | Individual value transformations | ValueTransformGroupId, InputPicklistValueId, OutputPicklistValueId |

## Runtime Objects (Execution)

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `FulfillmentPlan` | Runtime plan instance for an order | — |
| `FulfillmentStep` | Runtime step within a plan | FulfillmentPlanId, FulfillmentStepDefinitionId, AssignedToId (polymorphic, self-ref) |
| `FulfillmentStepDependency` | Runtime dependency between steps | FulfillmentStepId, DependsOnStepId, DependencyDefinitionId |
| `FulfillmentStepSource` | Source records for a step | — |
| `SalesTransactionFulfillReq` | Fulfillment request from a sales transaction | PlanId, PreviousRequestId (self-ref) |
| `SalesTrxnDeleteEvent` | Deletion events from transactions | — |

## Asset Decomposition Objects

| Object | Purpose | Key Fields |
|--------|---------|-----------|
| `FulfillmentAsset` | Decomposed asset during fulfillment | — |
| `FulfillmentAssetAttribute` | Attributes on fulfillment assets | — |
| `FulfillmentAssetRelationship` | Relationships between fulfillment assets | AssociatedFulfillmentAssetId |
| `AssetFulfillmentDecomp` | Decomposition mapping source → target assets | FulfillmentSourceAssetId, FulfillmentTargetAssetId |
| `FulfillmentLineAttribute` | Attributes on fulfillment lines | — |
| `FulfillmentLineRel` | Fulfillment line relationships | — |
| `FulfillmentLineSourceRel` | Source relationships for fulfillment lines | — |
| `ProdtDecompEnrchVarMap` | Variable mapping for decomposition enrichment | — |

## Key Relationships

```
FulfillmentStepDefinitionGroup ← FulfillmentStepDefinition (StepDefinitionGroupId)
FulfillmentStepDefinition ← FulfillmentStepDependencyDef (FulfillmentStepDefinitionId, DependsOnStepDefinitionId)
FulfillmentStepDefinitionGroup ← ProductFulfillmentScenario (FulfillmentStepDefnGroupId)
Product2 ← ProductFulfillmentDecompRule (SourceProductId, DestinationProductId)
FulfillmentPlan ← FulfillmentStep (FulfillmentPlanId)
FulfillmentStep ← FulfillmentStepDependency (FulfillmentStepId, DependsOnStepId)
FulfillmentAsset ← AssetFulfillmentDecomp (FulfillmentSourceAssetId, FulfillmentTargetAssetId)
FulfillmentAsset ← FulfillmentAssetRelationship (AssociatedFulfillmentAssetId)
ValTfrmGrp ← ProductDecompEnrichmentRule (ListMappingGroupId)
SalesTransactionFulfillReq ← SalesTransactionFulfillReq (PreviousRequestId, self-ref)
```

## SFDMU Data Plan: `qb-dro`

17 objects in 1 pass. Upstream: `qb-pcm` (Product2).

Design-time objects are loaded via data plan. Runtime objects (FulfillmentPlan, FulfillmentStep, etc.) are created at runtime during order processing.

User and Group objects are ReadOnly references for assignee resolution.
