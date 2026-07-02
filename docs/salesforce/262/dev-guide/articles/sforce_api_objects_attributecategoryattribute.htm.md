---
page_id: sforce_api_objects_attributecategoryattribute.htm
title: AttributeCategoryAttribute
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_attributecategoryattribute.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: pcm_std_objects_parent.htm
fetched_at: 2026-06-09
---

# AttributeCategoryAttribute

Represents a relationship between an attribute category and the attribute
definition. This object is available in API version 60.0 and later.

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
| AttributeCategoryId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The ID of the attribute category that the attribute is associated with. The ID is unique within the organization.  This field is a relationship field.  Relationship Name  AttributeCategory  Relationship Type  Lookup  Refers To  AttributeCategory |
| AttributeDefinitionId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The ID of the attribute definition associated with the attribute category. The ID is unique within the organization.  This field is a relationship field.  Relationship Name  AttributeDefinition  Relationship Type  Lookup  Refers To  AttributeDefinition |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the attribute category attribute was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the attribute category attribute was last viewed. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  A unique name for the attribute. The maximum length is 80 characters (of any type). |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The owner of the attribute category attribute.  This field is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[AttributeCategoryAttributeFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[AttributeCategoryAttributeHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.

[AttributeCategoryAttributeShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
