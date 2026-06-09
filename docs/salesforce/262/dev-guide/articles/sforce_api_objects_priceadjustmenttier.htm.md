---
page_id: sforce_api_objects_priceadjustmenttier.htm
title: PriceAdjustmentTier
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_priceadjustmenttier.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# PriceAdjustmentTier

Represents a discount tier in a price adjustment schedule.  This object
is available in API version 60.0 and later.

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

## Fields

| Field | Details |
| --- | --- |
| AdjustmentType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The type of price adjustment. |
| CurrencyIsoCode | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Available only if the multicurrency feature is enabled. Contains the ISO code for any currency allowed by the organization.  Possible values are:  - `BHD`—Bahraini   Dinar - `JPY`—Japanese   Yen - `USD`—U.S.   Dollar  The default value is `USD`. |
| EffectiveFrom | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time when the price adjustment tier comes into effect. |
| EffectiveTo | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time when the price adjustment tier remains effective. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Indicates when the user last referred to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed. |
| LowerBound | Type  double  Properties  Create, Filter, Sort, Update  Description  The minimum quantity the discount can be applied to. It must be a positive integer and less than or equal to the upper bound of the tier. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the price adjustment tier. |
| PriceAdjustmentScheduleId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the price adjustment schedule that the discount is applied to.  This field is a relationship field.  Relationship Name  PriceAdjustmentSchedule  Relationship Type  Lookup  Refers To  PriceAdjustmentSchedule |
| PricingTerm | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The number of pricing term units in the pricing term. Used with PricingTermUnit to define the length of the pricing term. For example, if PricingTermUnit is Months and this field is 1, the subscription is priced monthly.If the selling model is one-time, this field must be null. |
| PricingTermUnit | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The unit of time used to define the pricing term. Used with PricingTerm to define the length of the pricing term. For example, if this field is Months and PricingTerm is 1, the subscription is priced monthly. If the selling model is one-time, this field must be null.  Possible values are:  - `Annual`—Years - `Months` |
| Product2Id | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the product associated with the price adjustment tier.  This field is a relationship field.  Relationship Name  Product2  Relationship Type  Lookup  Refers To  Product2 |
| ProductSellingModelId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the ProductSellingModel record associated with this price adjustment tier record.  This field is a relationship field.  Relationship Name  ProductSellingModel  Relationship Type  Lookup  Refers To  ProductSellingModel |
| SellingModelType | Type  picklist  Properties  Defaulted on create, Filter, Group, Restricted picklist, Sort  Description  Indicates whether the product is sold as a one-time sale, an evergreen subscription, or a subscription with a defined term.  Possible values are:  - `Evergreen` - `OneTime`—One Time - `TermDefined`—Term-Defined  The default value is `OneTime`. |
| TierType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The unit of the discount. Possible values are:  - AdjustmentAmount—An amount discounted from an item’s list   price - AdjustmentPercentage—A percentage discounted from an item’s   list price  Possible values are:  - `AdjustmentAmount`—Amount - `AdjustmentPercentage`—Percentage - `OverrideAmount`—Override |
| TierValue | Type  double  Properties  Create, Filter, Sort, Update  Description  The value of the discount. |
| UpperBound | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  The maximum quantity the discount can be applied to. Must be a positive integer. Not inclusive. Set this value one digit higher than the quantity you want the tier to include. For example, if a tier’s upper bound is 99, set the value of UpperBound to 100. For the last tier, the value is optional. |

## Usage

To use PriceAdjustmentTiers, associate them with a PriceAdjustmentSchedule.

Tiers can’t overlap, and no gaps are allowed between tiers.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[PriceAdjustmentTierFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[PriceAdjustmentTierHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.
