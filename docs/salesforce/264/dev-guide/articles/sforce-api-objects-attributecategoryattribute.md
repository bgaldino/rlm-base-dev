---
page_id: sforce-api-objects-attributecategoryattribute
title: AttributeCategoryAttribute
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-attributecategoryattribute.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: pcm-std-objects-parent
legacy_page_id: sforce_api_objects_attributecategoryattribute.htm
fetched_at: 2026-11-25
---

# AttributeCategoryAttribute

Represents a relationship between an attribute category and the attribute definition. This object is available in API version 60.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

Product Catalog Management must be enabled to access this object.

## Fields

### AttributeCategoryId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The ID of the attribute category that the attribute is associated with. The ID is unique within the organization.

This field is a relationship field.

- **Relationship Name**: AttributeCategory

- **Relationship Type**: Lookup

- **Refers To**: AttributeCategory

### AttributeDefinitionId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The ID of the attribute definition associated with the attribute category. The ID is unique within the organization.

This field is a relationship field.

- **Relationship Name**: AttributeDefinition

- **Relationship Type**: Lookup

- **Refers To**: AttributeDefinition

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the attribute category attribute was last referenced.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the attribute category attribute was last viewed.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: A unique name for the attribute. The maximum length is 80 characters (of any type).

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The owner of the attribute category attribute.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Relationship Type**: Lookup

- **Refers To**: Group, User

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[AttributeCategoryAttributeFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[AttributeCategoryAttributeHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

**[AttributeCategoryAttributeShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-attributecategoryattribute.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
