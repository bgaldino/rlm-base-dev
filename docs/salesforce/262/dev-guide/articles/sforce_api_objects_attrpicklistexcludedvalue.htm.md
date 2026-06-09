---
page_id: sforce_api_objects_attrpicklistexcludedvalue.htm
title: AttrPicklistExcludedValue
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_attrpicklistexcludedvalue.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: pcm_std_objects_parent.htm
fetched_at: 2026-06-09
---

# AttrPicklistExcludedValue

Represents the excluded picklist values for a product classification
attribute or a product attribute definition. This object is available in API version
61.0 and later.

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
| AttributeId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the product classification attribute or the product attribute definition of the picklist data type.  This field is a polymorphic relationship field.  Relationship Name  Attribute  Relationship Type  Lookup  Refers To  ProductAttributeDefinition, ProductClassificationAttr |
| AttributePicklistValueId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the attribute picklist value that’s excluded in the product classification attribute or product attribute definition.  This field is a relationship field.  Relationship Name  AttributePicklistValue  Relationship Type  Lookup  Refers To  AttributePicklistValue |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the excluded attribute picklist value was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the excluded attribute picklist value was last viewed. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the excluded attribute picklist value. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The owner of the excluded attribute picklist value.  This field is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[AttrPicklistExcludedValueFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[AttrPicklistExcludedValueHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.

[AttrPicklistExcludedValueShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
