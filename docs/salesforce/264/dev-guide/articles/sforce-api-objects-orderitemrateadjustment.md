---
page_id: sforce-api-objects-orderitemrateadjustment
title: OrderItemRateAdjustment
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-orderitemrateadjustment.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: quote-and-order-capture-standard-objects
legacy_page_id: sforce_api_objects_orderitemrateadjustment.htm
fetched_at: 2026-11-25
---

# OrderItemRateAdjustment

Represents the negotiated rate adjustment for an order product. This object is available in API version 62.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Special Access Rules

## Fields

### AdjustmentType

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: Specifies the type of rate adjustment.

Possible values are `Amount`, `Override`, or `Percentage`

### AdjustmentValue

- **Type**: double

- **Properties**: Create, Filter, Sort, Update

- **Description**: The value of the adjustment.

### LowerBound

- **Type**: double

- **Properties**: Create, Filter, Sort, Update

- **Description**: The minimum quantity for the adjustment to be applicable.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The name of the order item rate adjustment.

### OrderItemRateCardEntryId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The parent order item rate card entry associated with the order item rate adjustment.

This field is a relationship field.

- **Relationship Name**: OrderItemRateCardEntry

- **Relationship Type**: Master-detail

- **Refers To**: OrderItemRateCardEntry (the master object)

### UpperBound

- **Type**: double

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The quantity below which the adjustment must be applicable. For example, if you want the adjustment to be applicable when the quantity is 99 or less, set this value to 100.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-orderitemrateadjustment.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
