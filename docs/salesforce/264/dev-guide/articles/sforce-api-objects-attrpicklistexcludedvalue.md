---
page_id: sforce-api-objects-attrpicklistexcludedvalue
title: AttrPicklistExcludedValue
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-attrpicklistexcludedvalue.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: pcm-std-objects-parent
legacy_page_id: sforce_api_objects_attrpicklistexcludedvalue.htm
fetched_at: 2026-11-25
---

# AttrPicklistExcludedValue

Represents the excluded picklist values for a product classification attribute or a product attribute definition. This object is available in API version 61.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

Product Catalog Management must be enabled to access this object.

## Fields

### AttributeId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The ID of the product classification attribute or the product attribute definition of the picklist data type.

This field is a polymorphic relationship field.

- **Relationship Name**: Attribute

- **Relationship Type**: Lookup

- **Refers To**: ProductAttributeDefinition, ProductClassificationAttr

### AttributePicklistValueId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The ID of the attribute picklist value that’s excluded in the product classification attribute or product attribute definition.

This field is a relationship field.

- **Relationship Name**: AttributePicklistValue

- **Relationship Type**: Lookup

- **Refers To**: AttributePicklistValue

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the excluded attribute picklist value was last referenced.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the excluded attribute picklist value was last viewed.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The name of the excluded attribute picklist value.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The owner of the excluded attribute picklist value.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Relationship Type**: Lookup

- **Refers To**: Group, User

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[AttrPicklistExcludedValueFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[AttrPicklistExcludedValueHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

**[AttrPicklistExcludedValueShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-attrpicklistexcludedvalue.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
