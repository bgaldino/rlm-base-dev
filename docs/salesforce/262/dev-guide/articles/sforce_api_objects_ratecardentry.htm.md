---
page_id: sforce_api_objects_ratecardentry.htm
title: RateCardEntry
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_ratecardentry.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Rate Management
parent_page: rate_management_std_objects_parent.htm
fetched_at: 2026-06-09
---

# RateCardEntry

Represents a rule that determines the charge rate for using a
product's resource. Each entry is linked to one rate card exclusively, and its activation
or deactivation can be controlled by assigning effective dates. This object is
available in API version 62.0 and later.

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
| DefaultUnitOfMeasureClassId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  ID of the default unit of measure classification record associated with this rate card entry.  This field is a relationship field.  Relationship Name  DefaultUnitOfMeasureClass  Refers To  UnitOfMeasureClass |
| DefaultUnitOfMeasureId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  ID of the default unit of measure record associated with this rate card entry.  This field is a relationship field.  Relationship Name  DefaultUnitOfMeasure  Refers To  UnitOfMeasure |
| EffectiveFrom | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  Date and time when the rate card entry comes into effect. |
| EffectiveTo | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  Date and time until when the rate card entry remains effective. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Timestamp for when the current user last referred to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Timestamp for when the current user last viewed a record related to this record. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Auto-generated identifier for the rate card entry record. |
| ProductId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  ID of the product whose resource is being used as a rate card entry.  This field is a relationship field.  Relationship Name  Product  Refers To  Product2 |
| ProductSellingModelId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  ID of the product selling model associated with this rate card entry.  This field is a relationship field.  Relationship Name  ProductSellingModel  Refers To  ProductSellingModel |
| Rate | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  Value of the rate card entry. |
| RateCardId | Type  reference  Properties  Create, Filter, Group, Sort  Description  ID of the rate card associated with this rate card entry.  This field is a relationship field.  Relationship Name  RateCard  Relationship Type  Master-detail  Refers To  RateCard (the master object) |
| RateCardType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Type of rate card associated with this rate card entry.  Valid values are:  - `Attribute` - `Base` - `Tier`  Available in API version 63.0 and later. |
| RateNegotiation | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  Type of rate negotiation applicable to the rate card entry.  Valid values are:  - `Negotiable` - `NonNegotiable`  The default value is `Negotiable`. Available in API version 63.0 and later. |
| RateUnitOfMeasureClassId | Type  reference  Properties  Filter, Group, Sort  Description  ID of the unit of measure classification record associated with this rate card entry.  This field is a relationship field.  Relationship Name  RateUnitOfMeasureClass  Refers To  UnitOfMeasureClass |
| RateUnitOfMeasureId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  ID of the standard unit of measure record associated with this rate card entry.  This field is a relationship field.  Relationship Name  RateUnitOfMeasure  Refers To  UnitOfMeasure |
| RateUnitOfMeasureName | Type  string  Properties  Filter, Group, Sort  Description  Name of the standard unit of measure record of the associated rate card entry. |
| Status | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  Status of the rate card entry.  - `Active` - `Draft` - `Inactive`  The default value is `Draft`. Available in API version 63.0 and later. |
| UsageProductId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  ID of the product associated with the resource for which the rate is specified.  This field is a relationship field.  Relationship Name  UsageProduct  Refers To  Product2 |
| UsageResourceId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  ID of the resource associated with this rate card entry.  This field is a relationship field.  Relationship Name  UsageResource  Refers To  UsageResource |

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re
available in the same API versions as this object. Otherwise, they’re available in the
specified API version and later.

[RateCardEntryFeed](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm)
:   Feed tracking is available for the object.

[RateCardEntryHistory](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm)
:   History is available for tracked fields of the object.
