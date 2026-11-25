---
page_id: sforce-api-objects-attributecategory
title: AttributeCategory
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-attributecategory.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: pcm-std-objects-parent
legacy_page_id: sforce_api_objects_attributecategory.htm
fetched_at: 2026-11-25
---

# AttributeCategory

Represents a logical grouping of attributes that can be reused while defining products. Attribute Categories are used for searching and managing product attributes. For example, the “Mobile Handset Properties” category has color, storage and make model, and size attributes. This object is available in API version 60.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

Product Catalog Management must be enabled to access this object.

## Fields

### Code

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Nillable, Sort, Update

- **Description**: The unique code for the attribute category. The maximum size is 80 alphanumeric characters. The code can include the following special characters: @ ! - < > * ? + = % # ( ) / \ & ‘ £ € $ ”.

### Description

- **Type**: textarea

- **Properties**: Create, Nillable, Update

- **Description**: The description of the attribute category that’s used only during design time.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the attribute category was last referenced.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the attribute category was last viewed.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The unique name of the attribute category. The maximum length is 80 characters (of any type).

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The owner of the attribute category.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Relationship Type**: Lookup

- **Refers To**: Group, User

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[AttributeCategoryFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[AttributeCategoryHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

**[AttributeCategoryShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-attributecategory.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
