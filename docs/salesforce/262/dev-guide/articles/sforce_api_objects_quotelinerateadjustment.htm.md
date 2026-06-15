---
page_id: sforce_api_objects_quotelinerateadjustment.htm
title: QuoteLineRateAdjustment
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_quotelinerateadjustment.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-06-09
---

# QuoteLineRateAdjustment

Represents the negotiated rate adjustment for a quote line item. This
object is available in API version 62.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`update()`,
`upsert()`

## Special Access Rules

This object is available with Revenue
Cloud.

## Fields

| Field | Details |
| --- | --- |
| AdjustmentType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Specifies the type of rate adjustment.  Possible values are:  - `Amount` - `Override` - `Percentage` |
| AdjustmentValue | Type  double  Properties  Create, Filter, Sort, Update  Description  The value of the adjustment. |
| LowerBound | Type  double  Properties  Create, Filter, Sort, Update  Description  The minimum quantity for the adjustment to be applicable. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the quote line rate adjustment record. |
| QuoteLineRateCardEntryId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The parent quote line rate card entry associated with the quote line rate adjustment.  This field is a relationship field.  Relationship Name  QuoteLineRateCardEntry  Relationship Type  Master-detail  Refers To  QuoteLineRateCardEntry (the master object) |
| UpperBound | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  The quantity below which the adjustment must be applicable. For example, if you want the adjustment to be applicable when the quantity is 99 or less, set this value to 100. |
