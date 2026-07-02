---
page_id: sforce_api_objects_assetstateperiod.htm
title: AssetStatePeriod
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_assetstateperiod.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-06-09
---

# AssetStatePeriod

Represents a time span when an asset has the same quantity, amount, and
monthly recurring revenue (MRR). An asset has as many asset state periods as there are
changes to it (asset actions) during its lifecycle. The dashboard and related pages show
the current asset state period. The fields can’t be edited. This object is available
in API version 50.0 and later.

## Supported Calls

`createable()`, `deletable()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `updateable()`.

## Special Access Rules

To use Customer Asset Lifecycle Management APIs,
you must have the Access Customer Asset Lifecycle Management APIs permission and Read
access to the Asset, Asset Action, Asset Action Source, and Asset State Period
objects.

## Fields

| Field | Details |
| --- | --- |
| Amount | Type  currency  Properties  Createable, Filter, Sort, Updateable  Description  An asset’s total amount during an asset state period. Revenue Cloud doesn't set or use this field's value currently. |
| AssetId | Type  reference  Properties  Createable, Filter, Group, Sort  Description  The asset related to an asset state period. Label is **Asset**.  This field is a relationship field.  Relationship Name  Asset  Relationship Type  Lookup  Refers To  Asset |
| AssetStatePeriodNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The ID of the asset state period. Label is **Name**. |
| BillingFrequency | Type  picklist  Properties  Createable, Filter, Group, Nillable, Restricted picklist, Sort, Updateable  Description  The time period that indicates how often the line item is billed.  Possible values are:  - `Annual` - `Monthly` - `Quarterly` - `Semi-Annual`  Available in API version 65.0 and later. |
| BindingInstanceTargetId | Type  reference  Properties  Createable, Filter, Group, Nillable, Sort, Updateable  Description  The ID of a custom product target for a usage-based quote line item, order Item, or asset allocation.  This field is a polymorphic relationship field.  Relationship Name  BindingInstanceTarget  Refers To  Account, Asset, BindingObjectCustomExt, Contract |
| Discount | Type  percent  Properties  Createable, Filter, Nillable, Sort, Updateable  Description  Editable number from 0 to 100. Available in API version 65.0 and later. |
| DiscountAmount | Type  currency  Properties  Createable, Filter, Nillable, Sort, Updateable  Description  The fixed amount discount to apply to the line item. Available in API version 65.0 and later. |
| EndDate | Type  dateTime  Properties  Createable, Filter, Nillable, Sort, Updateable  Description  The end date and time of an asset state period. On an asset that is an evergreen subscription, the last asset state period has no end date. |
| LegalEntityId | Type  reference  Properties  Createable, Filter, Group, Nillable, Sort, Updateable  Description  The ID of the related legal entity.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |
| Mrr | Type  currency  Properties  Createable, Filter, Sort, Updateable  Description  An asset’s monthly recurring revenue during an asset state period. |
| PriceRevisionPolicy | Type  reference  Properties  Createable, Filter, Group, Sort, Updateable  Description  Specifies the price uplift policy associated with this asset state period.  This field is a relationship field.  This field is available in API version 65.0 and later.  Relationship Name  Price Revision Policy  Relationship Type  Lookup  Refers To  PriceRevisionPolicy |
| Quantity | Type  double  Properties  Createable, Filter, Sort, Updateable  Description  The total quantity of an asset during an asset state period. |
| RampIdentifier | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The ramp record used to group order item segments for this asset state period.  This field is available in orgs that have Revenue Cloud when the Ramp Deals setting is enabled.  The maximum supported length is 255 characters from API version 67.0 and later.  This field is available in API version 62.0 and later. |
| SegmentIdentifier | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The order item segment for this asset state period.  This field is available in orgs that have Revenue Cloud when the Ramp Deals setting is enabled.  The maximum supported length is 255 characters from API version 67.0 and later.  This field is available in API version 62.0 and later. |
| SegmentName | Type  string  Properties  Createable, Filter, Group, Nillable, Sort, Updateable  Description  The name of the order item segment for this asset state period.  This field is available in orgs that have Revenue Cloud when the Ramp Deals setting is enabled.  The maximum supported length is 255 characters from API version 67.0 and later.  This field is available in API version 62.0 and later. |
| SegmentType | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Updateable  Description  The period for the order item segment for this asset state period. Valid values are:  - `Custom` - `Free Trial` - `Yearly`  The default value is `Yearly`.  This field is available in orgs that have Revenue Cloud when the Ramp Deals setting is enabled.  This field is available in API version 62.0 and later. |
| StartDate | Type  dateTime  Properties  Createable, Filter, Sort, Updateable  Description  The start date and time of an asset state period. |
| UnitPrice | Type  currency  Properties  Createable, Filter, Nillable, Sort, Updateable  Description  The price per unit for the line item. Available in API version 65.0 and later. Revenue Cloud won't populate this field in API version 66.0 and later. |
| UnitPriceUplift | Type  percent  Properties  Createable, Filter, Nillable, Sort, Updateable  Description  Indicates the percentage increase of a line item's unit price. Available in API version 65.0 and later. |
