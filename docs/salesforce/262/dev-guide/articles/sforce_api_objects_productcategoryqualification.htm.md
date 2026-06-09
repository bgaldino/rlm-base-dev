---
page_id: sforce_api_objects_productcategoryqualification.htm
title: ProductCategoryQualification
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productcategoryqualification.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: pcm_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProductCategoryQualification

Represents qualification rules for product categories. The rules determine
when the product category qualifies to be displayed to users. This object is available
in API version 60.0 and later.

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

| Field | Details |
| --- | --- |
| CategoryId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The product category associated with the category qualification record.  This field is a relationship field.  Relationship Name  Category  Relationship Type  Lookup  Refers To  ProductCategory |
| EffectiveFromDate | Type  date  Properties  Create, Filter, Group, Sort, Update  Description  The date from which the qualification rule for the product category comes into effect. |
| EffectiveToDate | Type  date  Properties  Create, Filter, Group, Sort, Update  Description  The date to which the qualification rule for the product category ceases to be in effect. |
| IsQualified | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the product category is qualified (`true`) or not (`false`) based on the qualification rules.  The default value is `false`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the product category qualification record was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the product category qualification record was last viewed. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the product category qualification record. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the owner of the product category qualification record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[ProductCategoryQualificationFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[ProductCategoryQualificationHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.

[ProductCategoryQualificationShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
