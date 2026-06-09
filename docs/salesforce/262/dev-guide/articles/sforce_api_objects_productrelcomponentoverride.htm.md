---
page_id: sforce_api_objects_productrelcomponentoverride.htm
title: ProductRelComponentOverride
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productrelcomponentoverride.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: pcm_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProductRelComponentOverride

Represents the cardinality overrides for product components in a bundle.
This object is available in API version 60.0 and later.

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
| DoesBundlePriceIncludeChild | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the bundle price includes the associated child component's price (`true`) or not (`false`).  The default value is `false`. |
| IsComponentRequired | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the component is a required component in the product bundle.  The default value is `false`. |
| IsDefaultComponent | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether this component is included in the product component group by default.  The default value is `false`. |
| IsExcluded | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the bundle excludes the component (`true`) or not (`false`).  The default value is `false`. |
| IsQuantityEditable | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the product component quantity can be edited (`true`) or not (`false`).  The default value is `false`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the product related component override record was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the product related component override record was last viewed. |
| MaxQuantity | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  The maximum quantity for the product component in the product bundle. |
| MinQuantity | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  The minimum quantity for the product component in the product bundle |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the product related component override. The maximum length is 255 characters (of any type). |
| OverrideContextId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID associated with the root product in a bundle.  This field is a polymorphic relationship field.  Relationship Name  OverrideContext  Relationship Type  Lookup  Refers To  Product2 |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The owner ID of the product related component override record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |
| ProductRelatedComponentId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID associated with the product related component record.  This field is a relationship field.  Relationship Name  ProductRelatedComponent  Relationship Type  Lookup  Refers To  ProductRelatedComponent |
| Quantity | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  The default number of child product related components. |
| QuantityScaleMethod | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The scaling method that determines how the child product quantity changes as the quantity of the parent product changes in the runtime cart.  Possible values are:  - `Constant` - `Proportional`  The default value is `Proportional`. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[ProductRelComponentOverrideFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[ProductRelComponentOverrideHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.

[ProductRelComponentOverrideShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
