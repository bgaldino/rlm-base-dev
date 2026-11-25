---
page_id: dynamic-revenue-orchestrator-std-objects-parent
title: Dynamic Revenue Orchestrator Standard Objects
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/dynamic-revenue-orchestrator-std-objects-parent.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-overview
legacy_page_id: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-11-25
---

# Dynamic Revenue Orchestrator Standard Objects

The Dynamic Revenue Orchestrator data model provides objects and fields to manage details of a product’s fulfillment.

- 

**[AssetFulfillmentDecomp](./sforce-api-objects-assetfulfillmentdecomp.md)**

Represents the relationship between an ordered asset and its corresponding fulfillment asset. This object is available in API version 62.0 and later.

- 

**[FulfillmentAsset](./sforce-api-objects-fulfillmentasset.md)**

Represents an instance of a technical product used to provide a customer asset. This object is available in API version 61.0 and later.

- 

**[FulfillmentAssetAttribute](./sforce-api-objects-fulfillmentassetattribute.md)**

Represents an attribute of a fulfillment asset. This object is available in API version 61.0 and later.

- 

**[FulfillmentAssetRelationship](./sforce-api-objects-fulfillmentassetrelationship.md)**

Represents a relationship between two fulfillment assets. This object is available in API version 61.0 and later.

- 

**[FulfillmentAssetStatePeriod](./sforce-api-objects-fulfillmentassetstateperiod.md)**

Represents the period during which the fulfillment asset configuration is applicable. This object is available in API version 67.0 and later.

- 

**[FulfmtAssetStatePeriodAttr](./sforce-api-objects-fulfillmentassetstateperiodattribute.md)**

Represents the key-value pair of a fulfillment asset attribute applicable during a specific asset state period. This object is available in API version 67.0 and later.

- 

**[FulfillmentFalloutRule](./sforce-api-objects-fulfillmentfalloutrule.md)**

Represents the fulfillment fallout handling rule. This object is available in API version 61.0 and later.

- 

**[FulfillmentLineAttribute](./sforce-api-objects-fulfillmentlineattribute.md)**

Represents an attribute of a fulfillment order line. This object is available in API version 61.0 and later.

- 

**[FulfillmentLineRel](./sforce-api-objects-fulfillmentlinerel.md)**

Represents a relationship between two fulfillment order lines. This object is available in API version 61.0 and later.

- 

**[FulfillmentLineSourceRel](./sforce-api-objects-fulfillmentlinesourcerel.md)**

Represents the relationship between a fulfillment order line and its decomposition source. This object is available in API version 61.0 and later.

- 

**[FulfillmentPlan](./sforce-api-objects-fulfillmentplan.md)**

Represents a set of steps to be created to fulfill the order. This object is available in API version 61.0 and later.

- 

**[FulfillmentStep](./sforce-api-objects-fulfillmentstep.md)**

Represents a task that’s required to perform a certain action as part of order fulfillment. This task can be manual or automated. This object is available in API version 61.0 and later.

- 

**[FulfillmentStepDefinition](./sforce-api-objects-fulfillmentstepdefinition.md)**

Represents a definition of a step that must be executed during fulfillment orchestration. This object is available in API version 61.0 and later.

- 

**[FulfillmentStepDefinitionGroup](./sforce-api-objects-fulfillmentstepdefinitiongroup.md)**

Represents a set of fulfillment step definitions. This object is available in API version 61.0 and later.

- 

**[FulfillmentStepDependency](./sforce-api-objects-fulfillmentstepdependency.md)**

Represents a dependency between tasks by defining the order between a task and one that depends on it. This object is available in API version 61.0 and later.

- 

**[FulfillmentStepDependencyDef](./sforce-api-objects-fulfillmentstepdependencydef.md)**

Represents a dependency that must be created between two fulfillment step records. This object is available in API version 62.0 and later.

- 

**[FulfillmentStepJeopardyRule](./sforce-api-objects-fulfillmentstepjeopardyrule.md)**

Represents the duration and tolerance for the step in the fulfillment process to allow the overall tracking of rules and risks. This object is available in API version 61.0 and later.

- 

**[FulfillmentStepSource](./sforce-api-objects-fulfillmentstepsource.md)**

Represents a link between a fulfillment step and the corresponding order lines. This object is available in API version 61.0 and later.

- 

**[FulfillmentTaskAssignmentRule](./sforce-api-objects-fulfillmenttaskassignmentrule.md)**

Represents a set of actions that assign a task to a user or queue. This object is available in API version 63.0 and later.

- 

**[FulfillmentWorkspace](./sforce-api-objects-fulfillmentworkspace.md)**

Represents a visual designer for fulfillment plans that can have multiple step groups and their dependencies. This object is available in API version 61.0 and later.

- 

**[FulfillmentWorkspaceItem](./sforce-api-objects-fulfillmentworkspaceitem.md)**

Represents information about the attributes that are used in the definition for a fulfillment step group. This object is available in API version 61.0 and later.

- 

**[ProductDecompEnrichmentRule](./sforce-api-objects-productdecompenrichmentrule.md)**

Represents mappings between fields and attributes. Enrichment rules are part of a decomposition rule, and are used to propagate data to fulfillment order lines. This object is available in API version 61.0 and later.

- 

**[ProdtDecompEnrchVarMap](./sforce-api-objects-prodtdecompenrchvarmap.md)**

Represents the mapping of a field context tag or an attribute to a variable within an expression set. This object is available in API version 64.0 and later.

- 

**[ProductFulfillmentDecompRule](./sforce-api-objects-productfulfillmentdecomprule.md)**

Represents a rule that determines how an order is broken into sub-orders with specific technical details that help in order fulfillment. It can be applied to a commercial or a technical product. This object is available in API version 61.0 and later.

- 

**[ProductFulfillmentScenario](./sforce-api-objects-productfulfillmentscenario.md)**

Represents a link between a product and the corresponding group of fulfillment steps that’s necessary to fulfill that product. This object is available in API version 61.0 and later.

- 

**[SalesTrxnDeleteEvent](./sforce-api-objects-salestrxndeleteevent.md)**

Represents the platform event that triggers the deletion of sales transaction fulfillment request records when the corresponding reference records are deleted. This object is available in API version 64.0 and later.

- 

**[SalesTransactionFulfillReq](./sforce-api-objects-salestransactionfulfillreq.md)**

Represents the statuses of all the sub-orders that belong to the selected commercial or technical product. This object is available in API version 62.0 and later.

- 

**[ValTfrm](./sforce-api-objects-valtfrm.md)**

Represents mappings between fields and attributes. Enrichment rules are part of a decomposition rule, and are used to propagate data to fulfillment order lines. This object is available in API version 61.0 and later.

- 

**[ValTfrmGrp](./sforce-api-objects-valtfrmgrp.md)**

Represents a rule that determines how an order is broken into sub-orders with specific technical details that help in order fulfillment. The rule can be applied to a commercial or a technical product. This object is available in API version 61.0 and later.

**See Also**

- [*Object Reference for the platform*: Overview of Salesforce Objects and Fields](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_concepts.htm)

- [*SOAP API Developer Guide*: Introduction to SOAP API](https://developer.salesforce.com/docs/atlas.en-us.api.meta/api/sforce_api_quickstart_intro.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/dynamic-revenue-orchestrator-std-objects-parent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
