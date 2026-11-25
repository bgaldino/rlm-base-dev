---
page_id: sforce-api-objects-fulfillmentlinesourcerel
title: FulfillmentLineSourceRel
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentlinesourcerel.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-std-objects-parent
legacy_page_id: sforce_api_objects_fulfillmentlinesourcerel.htm
fetched_at: 2026-11-25
---

# FulfillmentLineSourceRel

Represents the relationship between a fulfillment order line and its decomposition source. This object is available in API version 61.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

### Action

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort

- **Description**: Specifies the action to be performed on the asset fulfillment decomposition record. This field is available in API version 66.0 and later.

Possible values are:

- `Add`

- `Cancel`

- `NoChange`—No Change

### FulfilmentOrderLineId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The ID of the fulfillment order line.

This field is a relationship field.

- **Relationship Name**: FulfilmentOrderLine

- **Refers To**: FulfillmentOrderLineItem

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The relation between the two order line sources.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The ID of the user who created the relationship record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Refers To**: Group, User

### SourceItemIdentifier

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Nillable, Sort, Update

- **Description**: The ID of the decomposition source that’s related to the fulfilment order line. This field is available in API version 64.0 and later.

### SourceLineItemId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The ID of the source line item.

This field is a polymorphic relationship field.

- **Relationship Name**: SourceLineItem

- **Refers To**: FulfillmentOrderLineItem, OrderItem

### SourceType

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The type of source for the line item.

Valid values are `SourceBundleRoot` or `SourceLineItem`.

### SupplementalAction

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort

- **Description**: The supplemental action that’s applied to the line item based on the run-time changes made to the original fulfillment request. This field is available in API version 62.0 and later.

Valid values are:

- `Add`

- `Amend`

- `Cancel`

- `NoChange`

### UniqueIdentifier

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort

- **Description**: For internal use only.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[FulfillmentLineSourceRelShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentlinesourcerel.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
