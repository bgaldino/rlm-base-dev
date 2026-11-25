---
page_id: deployment-dynamic-revenue-orchestrator-objects
title: Dynamic Revenue Orchestrator Objects
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-dynamic-revenue-orchestrator-objects.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Revenue Management Deployment
parent_page: deployment-appendix-a
legacy_page_id: deployment_dynamic_revenue_orchestrator_objects.htm
fetched_at: 2026-11-25
---

# Dynamic Revenue Orchestrator Objects

This table provides the deployment sequence, object types, API names, and lookup fields for Dynamic Revenue Orchestrator objects in Revenue Management.

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

**See Also**

- [*Revenue Cloud Developer Guide*: Dynamic Revenue Orchestrator Standard Objects](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/dynamic_revenue_orchestrator_std_objects_parent.htm)

- [Explore the Revenue Cloud Data Model](https://help.salesforce.com/s/articleView?id=ind.data_model_overview.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-dynamic-revenue-orchestrator-objects.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
