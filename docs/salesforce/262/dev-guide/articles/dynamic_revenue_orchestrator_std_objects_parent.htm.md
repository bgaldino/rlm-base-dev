---
page_id: dynamic_revenue_orchestrator_std_objects_parent.htm
title: Dynamic Revenue Orchestrator Standard Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/dynamic_revenue_orchestrator_std_objects_parent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_overview.htm
fetched_at: 2026-06-09
---

# Dynamic Revenue Orchestrator Standard Objects

The Dynamic Revenue Orchestrator data model provides objects and fields to manage
details of a product’s fulfillment.

- **[AssetFulfillmentDecomp](./sforce_api_objects_assetfulfillmentdecomp.htm.md)**  
  Represents the relationship between an ordered asset and its corresponding fulfillment asset. This object is available in API version 62.0 and later.
- **[FulfillmentAsset](./sforce_api_objects_fulfillmentasset.htm.md)**  
  Represents an instance of a technical product used to provide a customer asset. This object is available in API version 61.0 and later.
- **[FulfillmentAssetAttribute](./sforce_api_objects_fulfillmentassetattribute.htm.md)**  
  Represents an attribute of a fulfillment asset. This object is available in API version 61.0 and later.
- **[FulfillmentAssetRelationship](./sforce_api_objects_fulfillmentassetrelationship.htm.md)**  
  Represents a relationship between two fulfillment assets. This object is available in API version 61.0 and later.
- **[FulfillmentAssetStatePeriod](./sforce_api_objects_fulfillmentassetstateperiod.htm.md)**  
  Represents the period during which the fulfillment asset configuration is applicable. This object is available in API version 67.0 and later.
- **[FulfmtAssetStatePeriodAttr](./sforce_api_objects_fulfillmentassetstateperiodattribute.htm.md)**  
  Represents the key-value pair of a fulfillment asset attribute applicable during a specific asset state period. This object is available in API version 67.0 and later.
- **[FulfillmentFalloutRule](./sforce_api_objects_fulfillmentfalloutrule.htm.md)**  
  Represents the fulfillment fallout handling rule. This object is available in API version 61.0 and later.
- **[FulfillmentLineAttribute](./sforce_api_objects_fulfillmentlineattribute.htm.md)**  
  Represents an attribute of a fulfillment order line. This object is available in API version 61.0 and later.
- **[FulfillmentLineRel](./sforce_api_objects_fulfillmentlinerel.htm.md)**  
  Represents a relationship between two fulfillment order lines. This object is available in API version 61.0 and later.
- **[FulfillmentLineSourceRel](./sforce_api_objects_fulfillmentlinesourcerel.htm.md)**  
  Represents the relationship between a fulfillment order line and its decomposition source. This object is available in API version 61.0 and later.
- **[FulfillmentPlan](./sforce_api_objects_fulfillmentplan.htm.md)**  
  Represents a set of steps to be created to fulfill the order. This object is available in API version 61.0 and later.
- **[FulfillmentStep](./sforce_api_objects_fulfillmentstep.htm.md)**  
  Represents a task that's required to perform a certain action as part of order fulfillment. This task can be manual or automated. This object is available in API version 61.0 and later.
- **[FulfillmentStepDefinition](./sforce_api_objects_fulfillmentstepdefinition.htm.md)**  
  Represents a definition of a step that must be executed during fulfillment orchestration. This object is available in API version 61.0 and later.
- **[FulfillmentStepDefinitionGroup](./sforce_api_objects_fulfillmentstepdefinitiongroup.htm.md)**  
  Represents a set of fulfillment step definitions. This object is available in API version 61.0 and later.
- **[FulfillmentStepDependency](./sforce_api_objects_fulfillmentstepdependency.htm.md)**  
  Represents a dependency between tasks by defining the order between a task and one that depends on it. This object is available in API version 61.0 and later.
- **[FulfillmentStepDependencyDef](./sforce_api_objects_fulfillmentstepdependencydef.htm.md)**  
  Represents a dependency that must be created between two fulfillment step records. This object is available in API version 62.0 and later.
- **[FulfillmentStepJeopardyRule](./sforce_api_objects_fulfillmentstepjeopardyrule.htm.md)**  
  Represents the duration and tolerance for the step in the fulfillment process to allow the overall tracking of rules and risks. This object is available in API version 61.0 and later.
- **[FulfillmentStepSource](./sforce_api_objects_fulfillmentstepsource.htm.md)**  
  Represents a link between a fulfillment step and the corresponding order lines. This object is available in API version 61.0 and later.
- **[FulfillmentTaskAssignmentRule](./sforce_api_objects_fulfillmenttaskassignmentrule.htm.md)**  
  Represents a set of actions that assign a task to a user or queue. This object is available in API version 63.0 and later.
- **[FulfillmentWorkspace](./sforce_api_objects_fulfillmentworkspace.htm.md)**  
  Represents a visual designer for fulfillment plans that can have multiple step groups and their dependencies. This object is available in API version 61.0 and later.
- **[FulfillmentWorkspaceItem](./sforce_api_objects_fulfillmentworkspaceitem.htm.md)**  
  Represents information about the attributes that are used in the definition for a fulfillment step group. This object is available in API version 61.0 and later.
- **[ProductDecompEnrichmentRule](./sforce_api_objects_productdecompenrichmentrule.htm.md)**  
  Represents mappings between fields and attributes. Enrichment rules are part of a decomposition rule, and are used to propagate data to fulfillment order lines. This object is available in API version 61.0 and later.
- **[ProdtDecompEnrchVarMap](./sforce_api_objects_prodtdecompenrchvarmap.htm.md)**  
  Represents the mapping of a field context tag or an attribute to a variable within an expression set. This object is available in API version 64.0 and later.
- **[ProductFulfillmentDecompRule](./sforce_api_objects_productfulfillmentdecomprule.htm.md)**  
  Represents a rule that determines how an order is broken into sub-orders with specific technical details that help in order fulfillment. It can be applied to a commercial or a technical product. This object is available in API version 61.0 and later.
- **[ProductFulfillmentScenario](./sforce_api_objects_productfulfillmentscenario.htm.md)**  
  Represents a link between a product and the corresponding group of fulfillment steps that's necessary to fulfill that product. This object is available in API version 61.0 and later.
- **[SalesTrxnDeleteEvent](./sforce_api_objects_salestrxndeleteevent.htm.md)**  
  Represents the platform event that triggers the deletion of sales transaction fulfillment request records when the corresponding reference records are deleted. This object is available in API version 64.0 and later.
- **[SalesTransactionFulfillReq](./sforce_api_objects_salestransactionfulfillreq.htm.md)**  
  Represents the statuses of all the sub-orders that belong to the selected commercial or technical product. This object is available in API version 62.0 and later.
- **[ValTfrm](./sforce_api_objects_valtfrm.htm.md)**  
  Represents mappings between fields and attributes. Enrichment rules are part of a decomposition rule, and are used to propagate data to fulfillment order lines. This object is available in API version 61.0 and later.
- **[ValTfrmGrp](./sforce_api_objects_valtfrmgrp.htm.md)**  
  Represents a rule that determines how an order is broken into sub-orders with specific technical details that help in order fulfillment. The rule can be applied to a commercial or a technical product. This object is available in API version 61.0 and later.

#### See Also

- [*Object Reference for the Salesforce Platform*: Overview of Salesforce Objects
  and Fields](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_concepts.htm "Object Reference for the Salesforce Platform: Overview of Salesforce Objects
         and Fields  - HTML (New Window)")
- [*SOAP API Developer Guide*: Introduction to SOAP API](https://developer.salesforce.com/docs/atlas.en-us.262.0.api.meta/api/sforce_api_quickstart_intro.htm "SOAP API Developer Guide: Introduction to SOAP API - HTML (New Window)")
