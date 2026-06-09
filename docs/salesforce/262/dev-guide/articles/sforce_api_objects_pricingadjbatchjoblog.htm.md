---
page_id: sforce_api_objects_pricingadjbatchjoblog.htm
title: PricingAdjBatchJobLog
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_pricingadjbatchjoblog.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# PricingAdjBatchJobLog

Represents the report that contains a list of failed adjustment requests
along with an error message that describes the reason for failure. This object is
available in API version 62.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where
possible, we changed noninclusive terms to align with our company value of Equality. We
maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| AdjustedValue | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  The adjusted value of a record. The stored value is used even if another pricing adjustment batch job is triggered again. |
| EffectiveFrom | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time when the failed versioned record is generated. This is only applicable for Price Adjustment records. |
| EffectiveTo | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time until when the failed versioned record is available. This is applicable only for Price Adjustment records. |
| ErrorCode | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The error code for the failure during the record update process. |
| ErrorMessage | Type  textarea  Properties  Create, Update  Description  The error message that’s generated for the failure during the record update process. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Indicates whether the pricing adjustment batch job has been archived (`true`) or not (`false`). This field is read-only. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. The name of the pricing adjustment batch job. |
| PricingAdjBatchJobId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The pricing adjustment batch job associated with the pricing adjustment batch job log.  This field is a relationship field.  Relationship Name  PricingAdjBatchJob  Relationship Type  Master-detail  Refers To  PricingAdjBatchJob (the master object) |
| TargetRecord | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The ID of the record for which a pricing adjustment error was generated. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[PricingAdjBatchJobLogFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[PricingAdjBatchJobLogHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.
