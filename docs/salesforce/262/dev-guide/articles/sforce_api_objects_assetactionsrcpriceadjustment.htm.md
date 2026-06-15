---
page_id: sforce_api_objects_assetactionsrcpriceadjustment.htm
title: AssetActionSrcPriceAdjustment
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_assetactionsrcpriceadjustment.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-06-09
---

# AssetActionSrcPriceAdjustment

Each row represents a junction between an asset and the calculated price
adjustment that's applied to an asset. This object is available in API version 66.0
and later.

## Supported Calls

`create()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`

## Fields

| Field | Details |
| --- | --- |
| AdjustmentValue | Type  double  Properties  Create, Filter, Nillable, Sort  Description  The value of the price adjustment that was applied to the asset. |
| AppliedPriceAdjustmentDate | Type  dateTime  Properties  Create, Filter, Sort  Description  The date and time on which the price adjustment was applied to the asset. |
| AssetActionSourceId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the asset action source related to the asset for which the price adjustment was applied.  This field is a relationship field.  Relationship Name  AssetActionSource  Relationship Type  Master-detail  Refers To  AssetActionSource (the master object) |
| AssetId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the asset that this price adjustment applies to.  This field is a relationship field.  Relationship Name  Asset  Refers To  Asset |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the asset price adjustment record. |
| PriceAdjustmentCauseId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the record that caused the price adjustment.  This field is a polymorphic relationship field.  Relationship Name  PriceAdjustmentCause  Refers To  Promotion |
| PriceAdjustmentSource | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort  Description  Specifies the source of price adjustment.  Possible values are:  - `Discretionary`—Reserved for future use. - `Promotion` - `Rule`—Reserved   for future use. - `System`—Reserved   for future use. |
| PrioritySequence | Type  int  Properties  Create, Filter, Group, Nillable, Sort  Description  The priority sequence of the applied price adjustment. |
