---
page_id: sforce_api_objects_fulfillmentassetstateperiodattribute.htm
title: FulfmtAssetStatePeriodAttr
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmentassetstateperiodattribute.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-11-23
---

# FulfmtAssetStatePeriodAttr

Represents the key-value pair of a fulfillment asset attribute applicable during a specific asset state period. This object is available in API version 67.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Special Access Rules

## Fields

### AttributeDefinitionId

- **Type**: reference
- **Properties**: Create, Filter, Group, Sort, Update
- **Description**: Represents the definition of the fulfillment asset state period attribute.

This field is a relationship field.

- **Relationship Name**: AttributeDefinition
- **Refers To**: AttributeDefinition

### AttributeName

- **Type**: string
- **Properties**: Filter, Group, idLookup, Nillable, Sort
- **Description**: Represents the name of the fulfillment asset state period attribute.

### AttributePicklistValueId

- **Type**: reference
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: Represents the reference identifier of the selected picklist value.

This field is a relationship field.

- **Relationship Name**: AttributePicklistValue
- **Refers To**: AttributePicklistValue

### AttributeValue

- **Type**: string
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: Represents the value of the fulfillment asset state period attribute.

### ExternalId

- **Type**: string
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: Represents the external ID of the fulfillment asset state period attribute.

### FulfillmentAssetStatePeriodId

- **Type**: reference
- **Properties**: Create, Filter, Group, Sort
- **Description**: Represents the fulfillment asset period applicable to the object.

This field is a relationship field.

- **Relationship Name**: FulfillmentAssetStatePeriod
- **Relationship Type**: Master-detail
- **Refers To**: FulfillmentAssetStatePeriod (the master object)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmentassetstateperiodattribute.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
