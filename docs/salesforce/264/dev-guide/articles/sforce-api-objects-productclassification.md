---
page_id: sforce-api-objects-productclassification
title: ProductClassification
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productclassification.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: pcm-std-objects-parent
legacy_page_id: sforce_api_objects_productclassification.htm
fetched_at: 2026-11-25
---

# ProductClassification

Represents a template that holds a collection of dynamic attributes. Product classification is used to quickly define and create multiple products that are similar yet different. This object is available in API version 60.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

Product Catalog Management must be enabled to access this object.

## Fields

### Code

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: A unique code for the product classification. The maximum size is 80 alphanumeric characters. The code can include the following special characters: @ ! - < > * ? + = % # ( ) / \ & ‘ £ € $ ”.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the product classification record was last referenced.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the product classification record was last viewed.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The name of the product classification. The maximum length is 80 characters (of any type).

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The owner of the product classification.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Relationship Type**: Lookup

- **Refers To**: Group, User

### Status

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: The lifecycle status of the product classification.

Possible values are:

- `Active`

- `Draft`

- `Inactive`

The default value is `Draft`.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[ProductClassificationFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[ProductClassificationHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

**[ProductClassificationShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productclassification.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
