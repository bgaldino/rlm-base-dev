---
page_id: sforce_api_objects_pricingadjbatchjob.htm
title: PricingAdjBatchJob
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_pricingadjbatchjob.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# PricingAdjBatchJob

Represents the collective update of multiple records on their prices
and other adjustments.  This object is available in API version 62.0 and
later.

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
| EffectiveFrom | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time when the updated value can be considered for a pricing adjustment batch job. |
| EffectiveTo | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time until when the updated value is effective and can be considered for a pricing adjustment batch job. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Indicates whether the pricing adjustment batch job has been archived (`true`) or not (`false`). This field is read-only. |
| LastTriggeredDate | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time when the pricing adjustment batch job was last triggered. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the pricing adjustment batch job. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The Salesforce ID of the sales representative who owns the pricing procedure resolution.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| ProcessedRecordsCount | Type  long  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The total number of records that were successfully updated. |
| RecordCount | Type  long  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The total number of records that have been processed. |
| RecordList | Type  textarea  Properties  Create  Description  The list of record IDs eligible for a pricing adjustment batch job. |
| ShouldSkipBulkRetry | Type  boolean  Properties  Create, Filter, Group, Nillable, Sort  Description  For internal use only. |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The processing status of the pricing adjustment batch job.  Valid values are:  - `Completed` - `Failed` - `InProgress` - `New` - `PartiallyCompleted` - `Rerun` |
| TargetObject | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort  Description  The target object of the pricing adjustment batch job.  Valid values are:  - `AttributeBasedAdjustment` - `BundleBasedAdjustment` - `PriceAdjustmentTier` - `PricebookEntry` |
| UpdateType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The type of update being made by the pricing adjustment batch job.  Valid values are:  - `Amount` - `Override` - `Percentage` |
| UpdateValue | Type  double  Properties  Create, Filter, Sort, Update  Description  The numerical value of the update. |

## Usage

To execute a pricing adjustment batch job through an API
request, make a POST request to the `/services/data/v67.0/sobjects/PricingAdjBatchJob` resource. Here's a sample
request payload.

```
{
  "TargetObject": "PriceAdjustmentTier",
  "UpdateType": "Amount",
  "UpdateValue": "10",
  "RecordList": "84YDU00000010ig2AA,84YDU00000010ig2AB,84YDU00000010ig2AC",
  "EffectiveFrom": "2024-08-01T10:07:09.000+0000",
  "EffectiveTo": "2024-08-05T10:07:09.000+0000"
}
```

You can specify a comma-separated list of record IDs that are eligible
for a pricing adjustment batch job.

To rerun a pricing adjustment batch job, make
a PATCH request to the `/services/data/v67.0/sobjects/PricingAdjBatchJob/pricingAdjBatchJobID`
resource. Here's a sample request
payload.

```
{
  "Status": "Rerun"
}
```

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[PricingAdjBatchJobFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[PricingAdjBatchJobHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.

[PricingAdjBatchJobShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
