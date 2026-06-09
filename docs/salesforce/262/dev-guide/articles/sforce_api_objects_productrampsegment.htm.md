---
page_id: sforce_api_objects_productrampsegment.htm
title: ProductRampSegment
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productrampsegment.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: pcm_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProductRampSegment

Represents the ramp period within a ramp deal where terms, volumes, and other
commitments change over time. This object is available in API version 62.0 and
later.

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
| DurationType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The unit of time within which users can try the product for free.  Valid values are:  - `Days` - `Months` |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the product ramp segment was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the product ramp segment was last viewed. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the product ramp segment. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the owner of the product ramp segment.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| ProductId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the product associated with the product ramp segment.  This field is a relationship field.  Relationship Name  Product  Refers To  Product2 |
| ProductSellingModelId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the product selling model associated with the product ramp segment.  This field is a relationship field.  Relationship Name  ProductSellingModel  Refers To  ProductSellingModel |
| SegmentType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  The time duration within the ramp deal where specific terms, volumes, and commitments are applied to the subscription product.  Valid values are:  - `Custom` - `FreeTrial` - `Yearly`  The default value is `Yearly`. |
| TrialDuration | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The duration within which users can try the product for free. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[ProductRampSegmentFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[ProductRampSegmentHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.

[ProductRampSegmentShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
