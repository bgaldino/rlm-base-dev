---
page_id: sforce-api-objects-fulfillmentlineattribute
title: FulfillmentLineAttribute
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentlineattribute.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-std-objects-parent
legacy_page_id: sforce_api_objects_fulfillmentlineattribute.htm
fetched_at: 2026-11-25
---

# FulfillmentLineAttribute

Represents an attribute of a fulfillment order line. This object is available in API version 61.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `query()`, `update()`, `upsert()`

## Fields

### AttributeDefinitionId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: A unique identifier for the attribute definition in the catalog.

This field is a relationship field.

- **Relationship Name**: AttributeDefinition

- **Refers To**: AttributeDefinition

### AttributeName

- **Type**: string

- **Properties**: Filter, Group, idLookup, Nillable, Sort

- **Description**: The name of the attribute.

### AttributePicklistValueId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: For internal use only.

This field is a relationship field.

- **Relationship Name**: AttributePicklistValue

- **Refers To**: AttributePicklistValue

### AttributeValue

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The value of the attribute.

### ExternalId

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The ID that uniquely identifies the relationship in an external data source.

### FulfillmentOrderLineItemId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: A unique identifier for the fulfillment order line item.

This field is a relationship field.

- **Relationship Name**: FulfillmentOrderLineItem

- **Relationship Type**: Master-detail

- **Refers To**: FulfillmentOrderLineItem (the master object)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentlineattribute.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
