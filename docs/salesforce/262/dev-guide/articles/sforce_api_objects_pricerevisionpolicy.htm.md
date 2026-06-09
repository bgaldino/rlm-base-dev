---
page_id: sforce_api_objects_pricerevisionpolicy.htm
title: PriceRevisionPolicy
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_pricerevisionpolicy.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# PriceRevisionPolicy

Represents the guidelines and methods used to modify product or service
prices, often incorporating formulas based on price revision entries and various
adjustments. For example, a policy might dictate that prices are revised based on a formula
that considers the regional Consumer Price Index (CPI) with a specific adjustment
percentage, effective from a defined date, and categorized as either a flat adjustment or
one directly based on the price revision entry data. This object is available in API
version 65.0 and later.

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
| EffectiveFrom | Type  date  Properties  Create, Filter, Group, Sort, Update  Description  The date and time when the price revision policy comes into effect. |
| EffectiveTo | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The date and time when the price revision policy is no longer in effect. |
| Formula | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The coded format of the formula used to calculate the revised price of a product from a quote and order, or contract. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the price revision policy. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  ID of the user who created the record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| PolicyType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The type of price revision policy.  Valid values are:  - `Flat`—You can’t   define a price index-based formula for revision. - `PriceIndex`—Price   Index |
| Region | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The region where the price revision policy is valid. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[PriceRevisionPolicyFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[PriceRevisionPolicyHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.

[PriceRevisionPolicyShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
