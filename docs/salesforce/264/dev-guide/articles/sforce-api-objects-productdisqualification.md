---
page_id: sforce-api-objects-productdisqualification
title: ProductDisqualification
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productdisqualification.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: pcm-std-objects-parent
legacy_page_id: sforce_api_objects_productdisqualification.htm
fetched_at: 2026-11-25
---

# ProductDisqualification

Represents disqualification rules for products. The rules determine when the product doesn’t qualify to be displayed to users. The rules are based on user context. This object is available in API version 60.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

Product Catalog Management must be enabled to access this object.

## Fields

### EffectiveFromDate

- **Type**: date

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The date from which the disqualification rule for the product comes into effect.

### EffectiveToDate

- **Type**: date

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The date to which the disqualification rule for the product ceases to be in effect.

### IsDisqualified

- **Type**: boolean

- **Properties**: Defaulted on create, Filter, Group, Sort

- **Description**: Indicates whether the product is disqualified based on the disqualification rules (`true`) or not (`false`).

The default value is `false`.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the product disqualification record was last referenced.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the product disqualification record was last viewed.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The name of the product disqualification record.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The owner of the product disqualification record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Relationship Type**: Lookup

- **Refers To**: Group, User

### ParentProductId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The ID of the immediate parent product in the product bundle hierarchy.

This field is a relationship field.

- **Relationship Name**: ParentProduct

- **Relationship Type**: Lookup

- **Refers To**: Product2

### ProductId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The product for which the disqualification rule is defined.

This field is a relationship field.

- **Relationship Name**: Product

- **Relationship Type**: Lookup

- **Refers To**: Product2

### Reason

- **Type**: textarea

- **Properties**: Create, Nillable, Update

- **Description**: The reason to disqualify the product.

### RootProductId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The ID of the root product in the product bundle hierarchy.

This field is a relationship field.

- **Relationship Name**: RootProduct

- **Relationship Type**: Lookup

- **Refers To**: Product2

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[ProductDisqualificationFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[ProductDisqualificationHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

**[ProductDisqualificationShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productdisqualification.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
