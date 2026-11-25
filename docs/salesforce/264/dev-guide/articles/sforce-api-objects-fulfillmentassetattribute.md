---
page_id: sforce-api-objects-fulfillmentassetattribute
title: FulfillmentAssetAttribute
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentassetattribute.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-std-objects-parent
legacy_page_id: sforce_api_objects_fulfillmentassetattribute.htm
fetched_at: 2026-11-25
---

# FulfillmentAssetAttribute

Represents an attribute of a fulfillment asset. This object is available in API version 61.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `query()`, `update()`, `upsert()`

## Fields

### AttributeDefinitionId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The attribute definition in the catalog.

This field is a relationship field.

- **Relationship Name**: AttributeDefinition

- **Relationship Type**: Lookup

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

- **Relationship Type**: Lookup

- **Refers To**: AttributePicklistValue

### AttributeValue

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The value of the attribute.

### ExternalId

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: For internal use only.

### FulfillmentAssetId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The identifier of the fulfillment asset.

This field is a relationship field.

- **Relationship Name**: FulfillmentAsset

- **Relationship Type**: Master-detail

- **Refers To**: FulfillmentAsset (the master object)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentassetattribute.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
