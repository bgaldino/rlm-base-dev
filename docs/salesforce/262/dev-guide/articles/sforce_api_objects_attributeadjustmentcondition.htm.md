---
page_id: sforce_api_objects_attributeadjustmentcondition.htm
title: AttributeAdjustmentCondition
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_attributeadjustmentcondition.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# AttributeAdjustmentCondition

Represents the condition applied to an attribute that determines the price of
a product or service being sold. This object is available in API version 60.0 and
later.

## Supported Calls

`create()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`search()`,
`update()`,
`upsert()`

## Fields

| Field | Details |
| --- | --- |
| AttributeBasedAdjRuleId | Type  reference  Properties  Create, Filter, Group, Sort  Description  Specifies the attribute adjustment rule record for which the condition is to be applied.  This field is a relationship field.  Relationship Name  AttributeBasedAdjRule  Relationship Type  Lookup  Refers To  AttributeBasedAdjRule |
| AttributeDefinitionId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  Specifies the attribute definition record for which the condition is to be applied.  This field is a relationship field.  Relationship Name  AttributeDefinition  Relationship Type  Lookup  Refers To  AttributeDefinition |
| BooleanValue | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies the boolean value of the operator.  Possible values are:  - `False` - `True` |
| DateTimeValue | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date time value of the attribute. |
| DateValue | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The date value of the attribute. |
| DoubleValue | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  The double value of the attribute. |
| IntegerValue | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The integer value of the attribute. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last referred to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Name of the attribute adjustment condition. |
| Operator | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  Operator used by the attribute.  Possible values are:  - `doesnotexistin`—Does Not Exist In - `equals`—Equals - `existsin`—Exists In - `greaterorequal`—Greater Or Equal - `greaterthan`—Greater Than - `lessorequal`—Less Or Equal - `lessthan`—Less Than - `matches`—Matches - `notequals`—Not Equals  The default value is `equals`. |
| ProductId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The ID of the product associated with the attribute adjustment condition.  This field is a relationship field.  Relationship Name  Product  Relationship Type  Lookup  Refers To  Product2 |
| StringValue | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The string value of the attribute. |
| UsageType | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  The type of record where the attribute adjustment condition is used.  Possible values are:  - `Pricing` - `Rating` |

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re
available in the same API versions as this object. Otherwise, they’re available in the
specified API version and later.

[AttributeAdjustmentConditionFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[AttributeAdjustmentConditionHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.
