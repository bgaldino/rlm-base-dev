---
page_id: sforce_api_objects_productattributedefinition.htm
title: ProductAttributeDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productattributedefinition.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: pcm_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProductAttributeDefinition

Represents the relationship between a product and its attributes. This
object is available in API version 60.0 and later.

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
| AttributeCategoryId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort  Description  The ID of the attribute category assigned to the parent object.  This field is a relationship field.  Relationship Name  AttributeCategory  Relationship Type  Lookup  Refers To  AttributeCategory |
| AttributeDefinitionId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the attribute associated with the product.  This field is a relationship field.  Relationship Name  AttributeDefinition  Relationship Type  Lookup  Refers To  AttributeDefinition |
| AttributeNameOverride | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The name to display for the attribute when shown for this object. This display name overrides the name on the attribute. For example, the attribute "Color" is overridden to display as "Laptop Color." The maximum size is 255 alphanumeric characters. The name can include these special characters: @ ! - < > \* ? + = % # ( ) / \ & ‘ £ € $ ”. |
| DefaultValue | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The default value for the product attribute. The attribute value can be changed. This default overrides the default value set for a picklist for the attribute. |
| Description | Type  textarea  Properties  Create, Nillable, Update  Description  A description of the attribute definition. The maximum size is 32,000 alphanumeric characters. The description can include these special characters: @ ! - < > \* ? + = % # ( ) / \ & ‘ £ € $ ”. |
| DisplayType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The type to display data for the selected data type.  Possible values are:  - `CheckBox`—Checkbox - `ComboBox`—Combobox - `Date` - `Datetime`—Date   Time - `Number` - `RadioButton`—Radio Button - `Slider`—Available   in API version 61.0 and later - `Text` - `Toggle` |
| HelpText | Type  textarea  Properties  Create, Nillable, Update  Description  The help text to display when end users are configuring this attribute. This field overrides the help text defined for the attribute itself. |
| IsHidden | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates if this product attribute is hidden from end users in the run time (`true`) or not (`false`).  The default value is `false`. |
| IsPriceImpacting | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether this attribute dictates the price of a product (`true`) or not (`false`).  The default value is `false`. |
| IsReadOnly | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the attribute is read-only for users in the run time (`true`) or not (`false`).  The default value is `false`. |
| IsRequired | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether this attribute requires a value when assigned to a parent object (`true`) or not (`false`).  The default value is `false`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the product attribute was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the product attribute was last viewed. |
| MaximumCharacterCount | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The maximum number of characters that can be entered for an attribute value. |
| MaximumValue | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The maximum value that can be entered as an attribute value. |
| MinimumCharacterCount | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The minimum number of characters that can be entered for an attribute value. |
| MinimumValue | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The minimum value that can be entered as an attribute value. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the product attribute. |
| OverriddenProductAttributeDefinitionId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort  Description  The ID associated with the overridden product attribute definition.  This field is a relationship field.  Relationship Name  OverriddenProductAttributeDefinition  Relationship Type  Lookup  Refers To  ProductAttributeDefinition |
| OverrideContextId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort  Description  The ID associated with the root product record in a bundle.  This field is a polymorphic relationship field.  Relationship Name  OverrideContext  Relationship Type  Lookup  Refers To  Product2 |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The owner of the product attribute definition.  This field is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |
| Product2Id | Type  reference  Properties  Create, Filter, Group, Sort  Description  The product ID associated with the product attribute definition.  This field is a relationship field.  Relationship Name  Product2  Relationship Type  Lookup  Refers To  Product2 |
| ProductClassificationAttributeId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the attribute assigned to the product classification.  This field is a relationship field.  Relationship Name  ProductClassificationAttribute  Relationship Type  Lookup  Refers To  ProductClassificationAttr |
| Sequence | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The display sequence of the attribute when configuring the product during run time. |
| Status | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The lifecycle state of the product attribute definition.  Valid values are:  - `Active` - `Draft` - `Inactive`  The default value is `Draft`. |
| StepValue | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The increment or decrement by which a slider's value changes as the user adjusts the product attribute value. Available in API version 61.0 and later. |
| ValueDescription | Type  textarea  Properties  Create, Nillable, Update  Description  The description of the value assigned to this attribute. This field takes on the value description from the attribute definition. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[ProductAttributeDefinitionFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[ProductAttributeDefinitionHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.

[ProductAttributeDefinitionShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
