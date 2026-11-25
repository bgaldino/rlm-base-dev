---
page_id: sforce-api-objects-productcategoryqualification
title: ProductCategoryQualification
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productcategoryqualification.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: pcm-std-objects-parent
legacy_page_id: sforce_api_objects_productcategoryqualification.htm
fetched_at: 2026-11-25
---

# ProductCategoryQualification

Represents qualification rules for product categories. The rules determine when the product category qualifies to be displayed to users. This object is available in API version 60.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

Product Catalog Management must be enabled to access this object.

## Fields

### CategoryId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The product category associated with the category qualification record.

This field is a relationship field.

- **Relationship Name**: Category

- **Relationship Type**: Lookup

- **Refers To**: ProductCategory

### EffectiveFromDate

- **Type**: date

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The date from which the qualification rule for the product category comes into effect.

### EffectiveToDate

- **Type**: date

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The date to which the qualification rule for the product category ceases to be in effect.

### IsQualified

- **Type**: boolean

- **Properties**: Defaulted on create, Filter, Group, Sort

- **Description**: Indicates whether the product category is qualified (`true`) or not (`false`) based on the qualification rules.

The default value is `false`.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the product category qualification record was last referenced.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the product category qualification record was last viewed.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The name of the product category qualification record.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The ID of the owner of the product category qualification record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Relationship Type**: Lookup

- **Refers To**: Group, User

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[ProductCategoryQualificationFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[ProductCategoryQualificationHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

**[ProductCategoryQualificationShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productcategoryqualification.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
