---
page_id: meta_orchestrationplanctxmapping.htm
title: OrchestrationPlanCtxMapping
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/meta_orchestrationplanctxmapping.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_metadata_api_parent.htm
fetched_at: 2026-11-23
---

# OrchestrationPlanCtxMapping

Represents the context mapping that Dynamic Revenue Orchestrator (DRO) uses to generate and orchestrate a plan for an object, such as a non-sales transaction for billing or another generic business process.

## Parent Type

[Metadata](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/metadata.htm "HTML (New Window)")
fullName

## File Suffix and Directory Location

OrchestrationPlanCtxMapping components have the suffix .orchestrationPlanCtxMapping and are stored in the orchestrationPlanCtxMappings folder.

## Version

OrchestrationPlanCtxMapping components are available in API version 67.0 and later.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| context​Definition | string | Required. [ContextDefinition](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/meta_contextdefinition.htm) that the orchestration use case is based on. |
| contextItem​Node | string | Name of the item-level node in the context definition. The item node represents the line items or child records of the root node, such as the items in an order. |
| contextMapping | string | Required. Name of the context mapping that maps the source object fields to the nodes in the context definition. |
| context​RootNode | string | Required. Name of the root node in the context definition. The root node represents the parent record that the orchestration plan is generated for, such as an order. |
| label | string | Required. UI label for the orchestration plan context mapping. |
| objectName | string | Required. API name of the object that the orchestration plan is generated for. The combination of objectName and orchestrationType must be unique. |
| orchestration​Type | PlanUsageType (enumeration of type string) | Required. Type of orchestration plan that this context mapping applies to. Valid values are `Billing`, `Fulfillment`, `Generic`, `IntegrationOrchestrator`, `InsuranceRuleAction`, `OrderFulfillment`, or `StageManagement`. |

## Declarative Metadata Sample Definition

This sample shows the definition of an OrchestrationPlanCtxMapping component for a fulfillment plan that orchestrates an order.

```
<?xml version="1.0" encoding="UTF-8"?>
<OrchestrationPlanCtxMapping xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>Order Fulfillment Context Mapping</label>
    <orchestrationType>Fulfillment</orchestrationType>
    <contextDefinition>SalesTransactionContext__stdctx</contextDefinition>
    <objectName>Order</objectName>
    <contextMapping>OrderEntitiesMapping</contextMapping>
    <contextRootNode>SalesTransaction</contextRootNode>
    <contextItemNode>SalesTransactionItem</contextItemNode>
</OrchestrationPlanCtxMapping>
```

This sample `package.xml` references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>OrchestrationPlanCtxMapping</name>
    </types>
    <version>68.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest file. For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/file_based.htm "HTML (New Window)").

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/meta_orchestrationplanctxmapping.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
