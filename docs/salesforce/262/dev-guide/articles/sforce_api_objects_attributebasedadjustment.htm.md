---
page_id: sforce_api_objects_attributebasedadjustment.htm
title: AttributeBasedAdjustment
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_attributebasedadjustment.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# AttributeBasedAdjustment

Represents the association between the product selling model and the price
adjustment for product or service being sold based on its attributes. This object stores
information about the attributes that define the price of the product or service, the
discounts applied, along with its value for a given date range. This object is
available in API version 60.0 and later.

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
| AdjustmentType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The type of pricing adjustment being made.  Possible values are:  - `Amount` - `Override` - `Percentage` |
| AdjustmentValue | Type  double  Properties  Create, Filter, Sort, Update  Description  The value of the adjustment being made based on the adjustment type. |
| AttributeBasedAdjRuleId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The attribute based adjustment rule associated with this attribute based adjustment record.  This field is a relationship field.  Relationship Name  AttributeBasedAdjRule  Relationship Type  Lookup  Refers To  AttributeBasedAdjRule |
| AttributeCount | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The number of attributes. |
| CurrencyIsoCode | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  ISO code of the currency. Must be one of the valid alphabetic, three-letter currency ISO codes defined by the ISO 4217 standard, such as USD, GBP, or JPY. Must be unique within your organization.  Possible values are:  - `BHD`—Bahraini Dinar - `JPY`—Japanese Yen - `USD`—U.S. Dollar  The default value is `USD`. |
| EffectiveFrom | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  The date and time when the price list entry comes into effect. |
| EffectiveTo | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time till when the price list entry remains effective. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date the attribute based adjustment was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Name of the attribute based adjustment. |
| PriceAdjustmentScheduleId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The price adjustment schedule associated with the attribute based adjustment record.  This field is a relationship field.  Relationship Name  PriceAdjustmentSchedule  Relationship Type  Lookup  Refers To  PriceAdjustmentSchedule |
| PricingTerm | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The number of pricing term units in the pricing term. Used with PricingTermUnit to define the length of the pricing term. For example, if PricingTermUnit is Months and this field is 1, the subscription is priced monthly.If the selling model is one-time, this field must be null. |
| PricingTermUnit | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The unit of time used to define the pricing term. Used with PricingTerm to define the length of the pricing term. For example, if this field is Months and PricingTerm is 1, the subscription is priced monthly. If the selling model is one-time, this field must be null.  Possible values are:  - `Annual`—Years - `Months` - `Quarterly` - `Semi-Annual` |
| ProductId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the product associated with the product attribute set.  This field is a relationship field.  Relationship Name  Product  Relationship Type  Lookup  Refers To  Product2 |
| ProductSellingModelId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort  Description  The ID of the ProductSellingModel record associated with this attribute based adjustment record.  This field is a relationship field.  Relationship Name  ProductSellingModel  Relationship Type  Lookup  Refers To  ProductSellingModel |
| SellingModelType | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates whether the product is sold as a one-time sale, an evergreen subscription, or a subscription with a defined term.  Possible values are:  - `Evergreen` - `OneTime`—One Time - `TermDefined`—Term-Defined  The default value is `OneTime`. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[AttributeBasedAdjustmentFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[AttributeBasedAdjustmentHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.
