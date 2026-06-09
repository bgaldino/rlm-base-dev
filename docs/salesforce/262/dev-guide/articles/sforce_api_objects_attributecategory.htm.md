---
page_id: sforce_api_objects_attributecategory.htm
title: AttributeCategory
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_attributecategory.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: pcm_std_objects_parent.htm
fetched_at: 2026-06-09
---

# AttributeCategory

Represents a logical grouping of attributes that can be reused while defining
products. Attribute Categories are used for searching and managing product attributes. For
example, the "Mobile Handset Properties" category has color, storage and make model, and
size attributes. This object is available in API version 60.0 and later.

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

Product Catalog Management must be enabled to
access this object.

## Fields

| Field | Details |
| --- | --- |
| Code | Type  string  Properties  Create, Filter, Group, idLookup, Nillable, Sort, Update  Description  The unique code for the attribute category. The maximum size is 80 alphanumeric characters. The code can include the following special characters: @ ! - < > \* ? + = % # ( ) / \ & ‘ £ € $ ”. |
| Description | Type  textarea  Properties  Create, Nillable, Update  Description  The description of the attribute category that's used only during design time. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the attribute category was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the attribute category was last viewed. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The unique name of the attribute category. The maximum length is 80 characters (of any type). |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The owner of the attribute category.  This field is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[AttributeCategoryFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[AttributeCategoryHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.

[AttributeCategoryShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
