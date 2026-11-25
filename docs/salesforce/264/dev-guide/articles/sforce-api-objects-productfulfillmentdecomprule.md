---
page_id: sforce-api-objects-productfulfillmentdecomprule
title: ProductFulfillmentDecompRule
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productfulfillmentdecomprule.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-std-objects-parent
legacy_page_id: sforce_api_objects_productfulfillmentdecomprule.htm
fetched_at: 2026-11-25
---

# ProductFulfillmentDecompRule

Represents a rule that determines how an order is broken into sub-orders with specific technical details that help in order fulfillment. It can be applied to a commercial or a technical product. This object is available in API version 61.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### ConditionData

- **Type**: textarea

- **Properties**: Create, Nillable, Update

- **Description**: The condition for executing the product fulfillment decomposition. The condition is defined as a rule or a set of rules in JSON format. This field is available in API version 66.0 and later.

### DestinationProductId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The destination product for the decomposition rule.

This field is a relationship field.

- **Relationship Name**: DestinationProduct

- **Relationship Type**: Lookup

- **Refers To**: Product2

### DestinationIdentifier

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Nillable, Sort, Update

- **Description**: The destination entity in the product fulfillment decomposition rule. This field can store a Salesforce product ID or an external identifier. This field is available in API version 65.0 and later.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The most recent date when a user referenced this record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The most recent date when a user viewed this record.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The name of the decomposition rule.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The ID of the user who created the record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Relationship Type**: Lookup

- **Refers To**: Group, User

### Priority

- **Type**: int

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The priority of the decomposition rule. Decomposition rules are executed in order of priority.

### SourceProductClassificationId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The classification of the source product that’s used for decomposition. This field is available in API version 62.0 and later.

This field is a relationship field.

- **Relationship Name**: SourceProductClassification

- **Refers To**: ProductClassification

### SourceClassIdentifier

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Nillable, Sort, Update

- **Description**: The source classification entity in the product fulfillment decomposition rule. This field can store a Salesforce product ID or an external identifier. This field is available in API version 65.0 and later.

### SourceIdentifier

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Nillable, Sort, Update

- **Description**: The source entity in the product fulfillment decomposition rule. This field can store a Salesforce product ID or an external identifier. This field is available in API version 65.0 and later.

### SourceProductId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: Source product for the decomposition rule.

This field is a relationship field.

- **Relationship Name**: SourceProduct

- **Relationship Type**: Lookup

- **Refers To**: Product2

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[ProductFulfillmentDecompRuleShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productfulfillmentdecomprule.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
