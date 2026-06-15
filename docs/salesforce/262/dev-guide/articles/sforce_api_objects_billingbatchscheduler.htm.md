---
page_id: sforce_api_objects_billingbatchscheduler.htm
title: BillingBatchScheduler
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_billingbatchscheduler.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# BillingBatchScheduler

Represents a scheduled processing job that triggers recurring invoice
batch runs. This object is available in API version 62.0 and later.

## Supported Calls

`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`search()`

## Special Access Rules

You need the Billing Admin permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| BillingSchedulerName | Type  string  Properties  Filter, Group, idLookup, Sort  Description  Required. The name of the scheduler. |
| Comments | Type  textarea  Properties  Filter, Nillable, Sort  Description  Additional details about the billing batch scheduler. |
| CronExpression | Type  string  Properties  Filter, Group, Sort  Description  Required. This field determines how often the scheduler recurs. |
| EndDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The date when the scheduler stops triggering batch processing jobs. |
| FrequencyCadence | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. The frequency of the scheduler triggering the invoice batch run.  Valid values are:  - `Daily`— The   scheduled job recurs every day. - `Monthly`— The   scheduled job recurs every month. - `Once`— The   scheduled job occurs one time and doesn’t recur. - `Weekly`— The   scheduled job recurs every week. |
| FrequencyOptions | Type  textarea  Properties  Nillable  Description  This field is a derived field that stores the scheduler configuration. |
| JobType | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. The type of batch processing job that the scheduler triggers.  Valid value is `Invoice` for which the scheduler starts a batch invoice run. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed a billing batch scheduler record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed a billing batch scheduler record. If this value is null, it’s possible that the user only accessed the billing batch scheduler record or a related list view (LastReferencedDate), but not viewed the billing batch scheduler record itself. |
| NextRunTime | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date and timestamp of the next scheduled batch invoice run in the user's time zone. |
| OwnerId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The ID of the user who created the scheduler.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| RecurringSubType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The frequency at which the batch processing job recurs when the FrequencyCadence field value is set to `Monthly`.  Valid values are:  - `Every`— The   processing job recurs at every instance of the frequency of   the value. For example, if the   RecurringSubType field value is   `Every` and the   FrequencyCadence field value is   `Weekly`, then the   batch processing job recurs every week. - `SpecificDate`—   The scheduler triggers the batch processing job on the   selected date. For example, if the selected date is 5, and   the FrequencyCadence field value is   `Monthly`, then the job   recurs on the fifth day of each month. |
| RecurringType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The frequency at which the batch processing job is repeated when the FrequencyCadence field value is set to `Weekly`.  Valid value is `Every`. |
| RecursOn | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The interval at which the scheduler triggers a batch processing job.  If the FrequencyCadence field value is `Monthly`, you must select either the specific date or the interval when the schedule triggers the job.  Valid values are:  - `First` - `Fourth` - `Last` - `Second` - `Third`  **Example:** To configure the scheduler to trigger the job on the first Monday of the month, set the following fields:  - FrequencyCadence=`Monthly` - RecursOn=`First` - RecursOnDay= `Monday` |
| RecursOnDate | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The date on which the scheduler triggers a batch processing job.  **Example:** To configure the scheduler to trigger the job on the fifth day of the month, set the following fields:  - FrequencyCadence=`Monthly` - RecursOnDate= 5  **Example:** To configure the scheduler to trigger the job on the second to last day of the month, set the following fields:  - FrequencyCadence=`Monthly` - RecursOnDate=`SecondToLast`  If you select `Last`, `SecondToLast`, or `ThirdToLast`, the date of the batch processing job varies depending on the number of days in the month.  For example, consider `SecondToLast` is selected. If the month has 30 days, such as June, then the batch processing job occurs on the 28th day. If the month has 31 days, such as July, then the batch processing job occurs on the 29th day. |
| RecursOnDay | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The day on which the scheduler triggers a batch processing job.  If the FrequencyCadence field value is set to `Weekly`, then you must select the day when the scheduler runs. The scheduler recurs every week on the selected day; for example, weekly on Monday.  Valid values are:  - `Sunday` - `Monday` - `Tuesday` - `Wednesday` - `Thursday` - `Friday` - `Saturday` |
| RunCriteriaId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The ID of the filter criteria that’s defined for the invoice batch run or the payment batch run.  This field is a polymorphic relationship field.  Relationship Name  RunCriteria  Refers To  InvoiceBatchRunCriteria |
| ShouldExcludeWkendAndHldy | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Required. Indicates whether weekends and holidays are excluded from the billing schedule (`true`) or not (`false`).  The default value is `false`. |
| ShouldStartRunImmediately | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Required. Indicates whether the invoice scheduler must start the run immediately (`true`) or not (`false`).  The default value is `false`. Available in API version 63.0 and later. |
| StartDate | Type  date  Properties  Filter, Group, Sort  Description  Required. The date when the scheduler triggers its first batch processing job. |
| StartTime | Type  time  Properties  Filter, Sort  Description  Required. The time when the scheduler triggers the batch processing job. |
| Status | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. The status of the scheduler. Only active schedulers can trigger batch processing jobs.  Valid values are:  - `Active` - `Canceled` - `Draft` - `Inactive` |
| TimeZone | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The time zone is either the value selected when the run was configured, or it's the user's time zone. The time zone is shown in Greenwich Mean Time (GMT). |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[BillingBatchSchedulerShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
