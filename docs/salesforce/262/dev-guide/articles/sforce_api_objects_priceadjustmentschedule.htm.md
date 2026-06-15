---
page_id: sforce_api_objects_priceadjustmentschedule.htm
title: PriceAdjustmentSchedule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_priceadjustmentschedule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# PriceAdjustmentSchedule

Represents a series of tiered discounts based on the number of items
purchased.  This object is available in API version 60.0 and later.

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
| AdjustmentMethod | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  The method for applying tiered pricing. Possible values are:  - Range—All items receive the discount of the highest tier the   quantity falls in. - Slab—Items receive the discount defined for the tier they   fall in.  Possible values are:  - `Range` - `Slab`  The default value is `Range`. |
| CurrencyIsoCode | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Available only if the multicurrency feature is enabled. Contains the ISO code for any currency allowed by the organization.  Possible values are:  - `BHD`—Bahraini Dinar - `JPY`—Japanese Yen - `USD`—U.S. Dollar  The default value is `USD`. |
| Description | Type  textarea  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Text description of the price adjustment schedule. |
| EffectiveFrom | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time when the price adjustment schedule comes into effect. |
| EffectiveTo | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time when the price adjustment schedule remains effective. |
| IsActive | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the price adjustment schedule is active (true) or not (false). You can change this field’s value as often as necessary. Label is **Active**. Default value is `False`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Indicates whether the price adjustment schedule has been archived (true) or not (false). This field is read-only. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  Required. The name of the price adjustment schedule. This field is read-only. Label is Price Adjustment Schedule Name. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The Salesforce ID of the sales representative who owns the price adjustment schedule.  This field is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |
| Pricebook2Id | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The price book associated with this price adjustment schedule record.  This field is a relationship field.  Relationship Name  Pricebook2  Relationship Type  Lookup  Refers To  Pricebook2 |
| ScheduleType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  The type of price adjustment schedule.  Possible values are:  - `Attribute` - `Bundle` - `Custom` - `Term` - `Volume`  The default value is `Volume`. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[PriceAdjustmentScheduleShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
