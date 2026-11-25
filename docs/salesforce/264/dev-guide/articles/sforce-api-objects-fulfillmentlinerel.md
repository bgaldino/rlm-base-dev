---
page_id: sforce-api-objects-fulfillmentlinerel
title: FulfillmentLineRel
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentlinerel.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-std-objects-parent
legacy_page_id: sforce_api_objects_fulfillmentlinerel.htm
fetched_at: 2026-11-25
---

# FulfillmentLineRel

Represents a relationship between two fulfillment order lines. This object is available in API version 61.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

### AssociatedFoItemInventory

- **Type**: picklist

- **Properties**: Filter, Group, Restricted picklist, Sort

- **Description**: Inventory level for the associated fulfillment order item.

Valid values are:

- `Included in Main Inventory`

- `Not Included in Main Inventory`

This field is available in API version 63.0 and later.

### AssociatedFulfillOrderItemId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The identifier of the associated fulfillment order line item.

This field is a relationship field.

- **Relationship Name**: AssociatedFulfillOrderItem

- **Refers To**: FulfillmentOrderLineItem

### AssociatedLineRole

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The role of the associated fulfillment order line item.

Valid values are `BundleComponent` or `ClassificationComponent`—Product Classification Component.

### AssociatedQuanScaleMethod

- **Type**: picklist

- **Properties**: Filter, Group, Restricted picklist, Sort

- **Description**: Method used to scale the quantity of the associated order item summary relative to the main fulfillment order item.

Valid values are:

- `Constant`

- `Proportional`

The default value is `Proportional`.

This field is available in API version 63.0 and later.

### FulfillmentOrderId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The ID of the parent fulfillment order.

This field is a relationship field.

- **Relationship Name**: FulfillmentOrder

- **Refers To**: FulfillmentOrder

### MainFulfillOrderItemRole

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The role of the primary fulfillment order line item.

Valid value is `Bundle`.

### MainFulfillmentOrderItemId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The ID of the associated fulfillment order line item.

This field is a relationship field.

- **Relationship Name**: MainFulfillmentOrderItem

- **Relationship Type**: Master-detail

- **Refers To**: FulfillmentOrderLineItem (the master object)

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The name of the fulfillment order line relationship.

### ProductRelationshipTypeId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The type of relationship between two assets.

This field is a relationship field.

- **Relationship Name**: ProductRelationshipType

- **Refers To**: ProductRelationshipType

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentlinerel.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
