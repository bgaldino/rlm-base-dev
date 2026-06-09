---
page_id: sforce_api_objects_productcomponentgrpoverride.htm
title: ProductComponentGrpOverride
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productcomponentgrpoverride.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: pcm_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProductComponentGrpOverride

Represents override information for a Product Component Group. The
cardinality of the product component group can be overridden in the context of a product
bundle. This object is available in API version 60.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`undelete()`,
`update()`,
`upsert()`

## Special Access Rules

Product Catalog Management must be enabled to
access this object.

## Fields

| Field | Details |
| --- | --- |
| IsExcluded | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the product component group is excluded from the product bundle in the runtime. Excluding a group automatically excludes all child components of the group.  The default value is `false`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the product component override record was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the product component override record was last viewed. |
| MaxBundleComponents | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The maximum number of components that can be added to a group. |
| MinBundleComponents | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The minimum number of components that must be added to a group. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the overridden product component group. |
| OverrideContextId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The root bundle product in whose context the group cardinality is overridden.  This field is a polymorphic relationship field.  Relationship Name  OverrideContext  Relationship Type  Lookup  Refers To  Product2 |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The owner of the product component group override record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |
| ProductComponentGroupId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the product component group record.  This field is a relationship field.  Relationship Name  ProductComponentGroup  Relationship Type  Lookup  Refers To  ProductComponentGroup |
