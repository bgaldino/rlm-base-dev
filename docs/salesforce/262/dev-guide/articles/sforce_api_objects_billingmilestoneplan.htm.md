---
page_id: sforce_api_objects_billingmilestoneplan.htm
title: BillingMilestonePlan
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_billingmilestoneplan.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# BillingMilestonePlan

Represents a structured approach to invoicing where invoices are
scheduled based on predefined milestones. This object is available in API version 63.0
and later.

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
| BillingTreatmentId | Type  reference  Properties  Create, Filter, Group, Sort  Description  Required. The billing treatment associated with the billing milestone plan.  This field is a relationship field.  Relationship Name  BillingTreatment  Refers To  BillingTreatment |
| Description | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Additional details about the billing milestone plan. |
| ExternalReference | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The external reference item that links a billing milestone plan item to the original transaction item. Available in API version 65.0 and later. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed a billing milestone plan record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed a billing milestone plan record. If this value is null, it’s possible that the user only accessed the billing milestone plan record or a related list view (`LastReferencedDate`), but not viewed the billing milestone plan record itself. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  Required. The name of the billing milestone plan. |
| ReferenceItemAmount | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  The total reference item amount to be billed. |
| ReferenceItemId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the reference item that links a billing milestone plan item to the original order item.  This field is a polymorphic relationship field.  Relationship Name  ReferenceItem  Refers To  BillingSchedule, OrderItem |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. The status of the billing milestone plan.  Valid values are:  - `Active` - `Cancelled` - `Completely Billed` - `Draft` |
