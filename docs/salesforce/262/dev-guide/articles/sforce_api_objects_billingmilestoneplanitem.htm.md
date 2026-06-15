---
page_id: sforce_api_objects_billingmilestoneplanitem.htm
title: BillingMilestonePlanItem
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_billingmilestoneplanitem.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# BillingMilestonePlanItem

Represents a specific billing milestone within the billing milestone
plan that’s used to manage and track billing based on the completion of certain
deliverables or stages. This object is available in API version 63.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

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

You need Revenue Cloud Billing license and the Billing Admin permission set to access
this object.

## Fields

| Field | Details |
| --- | --- |
| BillingMilestonePlanId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The billing milestone plan associated with the billing milestone plan item.  This field is a relationship field.  Relationship Name  BillingMilestonePlan  Relationship Type  Master-detail  Refers To  BillingMilestonePlan (the master object) |
| BillingScheduleGroupId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The billing schedule group that's related to the billing milestone plan item. Available in API version 64.0 and later.  This field is a relationship field.  Relationship Name  BillingScheduleGroup  Refers To  BillingScheduleGroup |
| CommencementDate | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The action that triggers the start of the billing milestone plan for a date-based milestone.  Valid value is:  - `OrderProductActivation` |
| CommencementDateOffset | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The offset applied to the commencement date to determine the milestone achievement date for a date-based milestone. |
| CommencementDateOffsetUnit | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The unit of time for the commencement date offset.  Valid values are:  - `Days` - `Months` - `Years` |
| Description | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Additional details about the billing milestone plan item. |
| FlatAmount | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  The amount in terms of units of currency, such as $10 or $21.52, to invoice from the order item. Used only when Type field has a value of `FlatAmount`. |
| IsMilestoneAccomplished | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Required. Indicates whether the billing treatment is for milestone billing (`true`) or not (`false`). |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed a billing milestone plan item record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed a billing milestone plan item record. If this value is null, it’s possible that the user only accessed the billing milestone plan item record or a related list view (LastReferencedDate), but not viewed the billing milestone plan item record itself. |
| MilestoneAccomplishmentDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The date the milestone is achieved for date-based milestones. For event-based milestones, this field indicates the date when the milestone is manually marked as completed. |
| MilestoneAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The amount that’s billed when the milestone is reached or completed. |
| MilestoneType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The milestone type for the billing treatment item.  Valid values are:  - `Date` - `Event` |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  Required. The name of the billing milestone plan item. |
| Percentage | Type  percent  Properties  Create, Filter, Nillable, Sort, Update  Description  The percentage,such as 10% or 12.5%, to invoice from the order item. Used only when Type field has a value of `Percentage`. |
| ServicePeriodEnd | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The end date of the service associated with the milestone.  Valid value is:  - `Order Product End   Date` |
| ServicePeriodStart | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The start date of the service associated with the milestone.  Valid value is:  - `Order Product Start   Date` |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The status of the billing milestone plan item.  Valid values are:  - `Cancelled` - `Draft` - `Error` - `Invoiced` - `Ready for   Invoicing` - `Waiting for Milestone   Accomplishment` |
| Type | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. Specifies whether billing schedules created from this billing treatment item are based on a flat amount or a percentage of the order item's total amount.  Valid values are:  - `FlatAmount` - `Percentage` - `Remainder` |
