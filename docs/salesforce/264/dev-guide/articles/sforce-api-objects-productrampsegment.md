---
page_id: sforce-api-objects-productrampsegment
title: ProductRampSegment
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productrampsegment.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: pcm-std-objects-parent
legacy_page_id: sforce_api_objects_productrampsegment.htm
fetched_at: 2026-11-25
---

# ProductRampSegment

Represents the ramp period within a ramp deal where terms, volumes, and other commitments change over time. This object is available in API version 62.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

Product Catalog Management must be enabled to access this object.

## Fields

### DurationType

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: The unit of time within which users can try the product for free.

Valid values are:

- `Days`

- `Months`

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the product ramp segment was last referenced.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the product ramp segment was last viewed.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The name of the product ramp segment.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The ID of the owner of the product ramp segment.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Refers To**: Group, User

### ProductId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The ID of the product associated with the product ramp segment.

This field is a relationship field.

- **Relationship Name**: Product

- **Refers To**: Product2

### ProductSellingModelId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The ID of the product selling model associated with the product ramp segment.

This field is a relationship field.

- **Relationship Name**: ProductSellingModel

- **Refers To**: ProductSellingModel

### SegmentType

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The time duration within the ramp deal where specific terms, volumes, and commitments are applied to the subscription product.

Valid values are:

- `Custom`

- `FreeTrial`

- `Yearly`

The default value is `Yearly`.

### TrialDuration

- **Type**: int

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The duration within which users can try the product for free.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[ProductRampSegmentFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[ProductRampSegmentHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

**[ProductRampSegmentShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productrampsegment.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
