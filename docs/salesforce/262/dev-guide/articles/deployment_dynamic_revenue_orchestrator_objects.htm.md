---
page_id: deployment_dynamic_revenue_orchestrator_objects.htm
title: Dynamic Revenue Orchestrator Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_dynamic_revenue_orchestrator_objects.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_appendix_A.htm
fetched_at: 2026-06-09
---

# Dynamic Revenue Orchestrator Objects

This table provides the deployment sequence, object types, API names, and lookup fields
for Dynamic Revenue Orchestrator objects in Revenue Cloud.

| Object Use Type | Object Name | Object API | Deployment Sequence | Lookup Fields (Foreign Keys) |
| --- | --- | --- | --- | --- |
| Configuration | Fulfillment Step Definition Group | FulfillmentStepDefinitionGroup | 1 | None |
| Configuration | Fulfillment Step Definition | FulfillmentStepDefinition | 2 | Ruleset, ExpressionSet, FulfillmentStepDefinitionGroup, IntegrationProviderDef, User, Queue |
| Configuration | Fulfillment Step Dependency Definition | FulfillmentStepDependencyDef | 3 | FulfillmentStepDefinition |
| Configuration | Product Fulfillment Scenario | ProductFulfillmentScenario | 4 | FulfillmentStepDefinitionGroup, Ruleset, Product2, ProductClassification, FlowDefinition, StageDefinition, FlowRecord, FlowOrchestration |
| Configuration | Fulfillment Workspace | FulfillmentWorkspace | 5 | None |
| Configuration | Fulfillment Workspace Item | FulfillmentWorkspaceItem | 6 | FulfillmentWorkspace, FulfillmentStepDefinitionGroup |
| Configuration | Fulfillment Fallout Rule | FulfillmentFalloutRule | 7 | IntegrationProviderDef, Group |
| Configuration | Fulfillment Step Jeopardy Rule | FulfillmentStepJeopardyRule | 8 | IntegrationProviderDef |
| Configuration | Fulfillment Task Assignment Rule | FulfillmentTaskAssignmentRule | 9 | Ruleset, ExpressionSet, User, Queue |
| Configuration | Product Fulfillment Decomposition Rule | ProductFulfillmentDecompRule | 1 | Ruleset, Product2, ProductClassification |
| Configuration | Value Transformation Group | ValTfrmGrp | 2 | None |
| Configuration | Value Transformation | ValTfrm | 3 | ValTfrmGrp, AttributePicklistValue |
| Configuration | Product Decomposition Enrichment Rule | ProductDecompEnrichmentRule | 4 | ProductFulfillmentDecompRule, ExpressionSet, AttributeDefinition, ValTfrmGrp, DecisionMatrixDefinition |
| Configuration | Product Decomposition Enrichment Variable Mapping | ProdtDecompEnrchVarMap | 5 | ProductDecompEnrichmentRule, AttributeDefinition |

#### See Also

- [*Revenue Cloud Developer Guide*: Dynamic Revenue Orchestrator Standard
  Objects](./dynamic_revenue_orchestrator_std_objects_parent.htm.md "Revenue Cloud Developer Guide: Dynamic Revenue Orchestrator Standard
         Objects - HTML (New Window)")
- [Explore the Revenue Cloud Data Model](https://help.salesforce.com/s/articleView?id=ind.data_model_overview.htm&language=en_US "Explore the Revenue Cloud Data Model - HTML (New Window)")
