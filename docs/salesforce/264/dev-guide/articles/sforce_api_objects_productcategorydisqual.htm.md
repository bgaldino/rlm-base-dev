---
page_id: sforce_api_objects_productcategorydisqual.htm
title: ProductCategoryDisqual
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productcategorydisqual.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: pcm_std_objects_parent.htm
fetched_at: 2026-11-23
---

# ProductCategoryDisqual

Represents disqualification rules for product categories. The rules determine
when the product category doesn’t qualify to be displayed to users. This object is
available in API version 60.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`search()`,
`undelete()`,
`update()`,
`upsert()`

## Special Access Rules

Product Catalog Management must be enabled to access this object.

## Fields

### CategoryId

- **Type**: reference
- **Properties**: Create, Filter, Group, Sort, Update
- **Description**: The product category associated with the product disqualification record.

This field is a relationship field.

- **Relationship Name**: Category
- **Relationship Type**: Lookup
- **Refers To**: ProductCategory

### EffectiveFromDate

- **Type**: date
- **Properties**: Create, Filter, Group, Sort, Update
- **Description**: The date from which the disqualification rule for the product category comes into effect.

### EffectiveToDate

- **Type**: date
- **Properties**: Create, Filter, Group, Sort, Update
- **Description**: The date to which the disqualification rule for the product category ceases to be in effect.

### IsDisqualified

- **Type**: boolean
- **Properties**: Defaulted on create, Filter, Group, Sort
- **Description**: Indicates whether the product category is disqualified (`true`) or not (`false`) based on the disqualification rules.

The default value is `false`.

### LastReferencedDate

- **Type**: dateTime
- **Properties**: Filter, Nillable, Sort
- **Description**: The date the product category disqualification record was last referenced.

### LastViewedDate

- **Type**: dateTime
- **Properties**: Filter, Nillable, Sort
- **Description**: The date the product category disqualification record was last viewed.

### Name

- **Type**: string
- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort
- **Description**: The name of the product category disqualification record.

### OwnerId

- **Type**: reference
- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update
- **Description**: The ID of the owner of the product category disqualification record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner
- **Relationship Type**: Lookup
- **Refers To**: Group, User

### Reason

- **Type**: string
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The reason to disqualify the product category.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

**[ProductCategoryDisqualFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object."):** Feed tracking is available for the object.

**[ProductCategoryDisqualHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object."):** History is available for tracked fields of the object.

**[ProductCategoryDisqualShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object."):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productcategorydisqual.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
