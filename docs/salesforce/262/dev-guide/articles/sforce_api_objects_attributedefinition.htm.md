---
page_id: sforce_api_objects_attributedefinition.htm
title: AttributeDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_attributedefinition.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# AttributeDefinition

Represents a product, asset, or object attribute, for example, a hardware
specification or software detail. This object is available in API version 60.0 and
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

## Fields

| Field | Details |
| --- | --- |
| Code | Type  string  Properties  Create, Filter, Group, idLookup, Nillable, Sort, Update  Description  Code for the attribute definition. This field is unique within your organization. |
| CurrencyIsoCode | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Available only if the multicurrency feature is enabled. Contains the ISO code for any currency allowed by the organization.  Possible values are:  - `BHD`—Bahraini Dinar - `JPY`—Japanese Yen - `USD`—U.S. Dollar  The default value is `USD`. |
| DataType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort  Description  The data type of the attribute definition.  Possible values are:  - `Checkbox` - `Currency` - `Date` - `Datetime` - `Multipicklist` - `Number` - `Percent` - `Picklist` - `Text` |
| DefaultHelpText | Type  textarea  Properties  Create, Nillable, Update  Description  The default help text for this attribute. |
| DefaultValue | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The default value for this attribute. |
| Description | Type  textarea  Properties  Create, Nillable, Update  Description  Description of this attribute. |
| DeveloperName | Type  string  Properties  Create, Filter, Group, Sort  Description  The unique name of the attribute definition record.  This name must begin with a letter and use only alphanumeric characters and underscores. It can't include spaces, end with an underscore, or have two consecutive underscores. |
| IsActive | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates that the attribute definition is active. Active attributes definitions can be selected for products.  The default value is `false`. |
| IsRequired | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the attribute definition is required for a product.  The default value is `false`. |
| Label | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The label for the attribute. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the attribute definition was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the attribute definition was last viewed. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the attribute. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The owner of the attribute definition.  This field is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |
| PicklistId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort  Description  The ID of the attribute picklist with the valid values for this attribute.  This field is a relationship field.  Relationship Name  Picklist  Relationship Type  Lookup  Refers To  AttributePicklist |
| SourceSystemIdentifier | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The identifier of the attribute definition in an external system. |
| ValueDescription | Type  textarea  Properties  Create, Nillable, Update  Description  The default value description for this attribute. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[AttributeDefinitionFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[AttributeDefinitionHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.

[AttributeDefinitionShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
