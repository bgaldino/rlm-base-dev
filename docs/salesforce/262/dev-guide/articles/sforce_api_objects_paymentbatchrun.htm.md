---
page_id: sforce_api_objects_paymentbatchrun.htm
title: PaymentBatchRun
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_paymentbatchrun.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# PaymentBatchRun

Represents a batch processing job that processes payments in Billing. During
a payment batch run, all the payment schedules that meet the specified criteria are
processed and the corresponding Payment records are created. These payments are then
applied to invoices or invoice lines. This object is available in API version 64.0 and
later.

## Supported Calls

`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`update()`

## Special Access Rules

You need the Revenue Cloud Billing license, and the Payment Admin permission set or the
Payment Operations User permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| BillingBatchSchedulerId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  Required. The ID of the billing batch scheduler that's used to schedule the payment batch run.  This field is a relationship field.  Relationship Name  BillingBatchScheduler  Refers To  BillingBatchScheduler |
| Comments | Type  textarea  Properties  Filter, Nillable, Sort, Update  Description  Additional details about the payment batch run. |
| CompletionTime | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date and time when the payment batch run completed processing payments. |
| IsPaymentRetry | Type  boolean  Properties  Filter, Nillable, Sort  Description  Indicates whether the payment batch run is for retrying a failed payment (`true`) or not (`false`).  The default value is `false`. Available in API version 66.0 and later. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed this record or list view. If this value is null, and LastReferenceDate is not null, the user accessed this record or list view indirectly. |
| OwnerId | Type  reference  Properties  Filter, Group, Sort, Update  Description  Required. The ID of the owner of the Payment Batch Run record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| PaymentBatchRunNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. The auto-generated reference number for the payment batch run. |
| StartTime | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date and time when the payment batch run started processing payments. |
| Status | Type  picklist  Properties  Defaulted on create, Filter, Group, Restricted picklist, Sort  Description  Required. The status of the payment batch run.  Valid values are:  - `Completed` - `Failed` - `New` - `Started` - `Stopped`  The default value is `New`. |
| TotalFailedScheduleItems | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The total number of payment schedules that weren’t processed by the payment batch run. When a payment schedule isn’t processed, the system doesn’t generate a Payment record for it. For details about errors, check the Revenue Transaction Error Log records for the payment batch run. |
| TotalFilteredScheduleItems | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The total number of payment schedule items that meet the payment run scheduler’s matching criteria. The matching criteria identifies the payment schedule items that are included for processing by the payment batch run. |
| TotalProcessedScheduleItems | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The total number of payment schedule items that were processed by the payment batch run. |
| TotalScheduleItemsApplied | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The total number of payment schedule items that were processed and had corresponding payments also applied to invoices or invoice lines. |
| TotalScheduleItemsApplyFailed | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The total number of payment schedule items that were processed but had corresponding payments that weren't applied to invoices or invoice lines. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[PaymentBatchRunShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
