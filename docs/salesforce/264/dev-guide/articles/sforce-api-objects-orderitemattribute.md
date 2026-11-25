---
page_id: sforce-api-objects-orderitemattribute
title: OrderItemAttribute
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-orderitemattribute.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: quote-and-order-capture-standard-objects
legacy_page_id: sforce_api_objects_orderitemattribute.htm
fetched_at: 2026-11-25
---

# OrderItemAttribute

Represents a virtual object that stores an attribute specified for an order item.This object is available in API version 60.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Special Access Rules

This object is available in Enterprise, Unlimited, and Developer Editions of Revenue Cloud.

## Fields

### AttributeDefinitionId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The ID of the attribute definition for this order item attribute.

This field is a relationship field.

- **Relationship Name**: AttributeDefinition

- **Relationship Type**: Lookup

- **Refers To**: AttributeDefinition

### AttributeName

- **Type**: string

- **Properties**: Filter, Group, idLookup, Nillable, Sort

- **Description**: The name given to order item attribute.

### AttributePicklistValueId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The ID of the attribute picklist value if the attribute is a picklist type.

This field is a relationship field.

- **Relationship Name**: AttributePicklistValue

- **Relationship Type**: Lookup

- **Refers To**: AttributePicklistValue

### AttributeValue

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: Stores the value of the order item attribute. For example 5-TB storage.

You can use this field to filter records only if the DataType value in the related `AttributeDefinitionId` record is `Text`. If the DataType value is `Picklist`, use the value in the `AttributePicklistValueId` field for filtering. You can’t use this field to filter records if the DataType value is `Checkbox`, `Currency`, `Date`, `Datetime`, `Multipicklist`, `Number`, or `Percent`.

### ExternalId

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: An auto-generated ID of the attribute record saved in an external system (for example an HBase database).

### IsPriceImpacting

- **Type**: boolean

- **Properties**: Defaulted on create, Filter, Group, Sort

- **Description**: The pricing impacting the status of the attribute.

The default value is `false`.

### OrderItemId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The parent order item associated with the order item attribute.

This field is a relationship field.

- **Relationship Name**: OrderItem

- **Relationship Type**: Lookup

- **Refers To**: OrderItem

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-orderitemattribute.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
