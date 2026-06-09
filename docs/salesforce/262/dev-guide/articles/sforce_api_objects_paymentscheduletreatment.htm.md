---
page_id: sforce_api_objects_paymentscheduletreatment.htm
title: PaymentScheduleTreatment
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_paymentscheduletreatment.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# PaymentScheduleTreatment

Represents information about the processing of payment schedules including
the payment method and the payment amount for the payment schedule. This object is
available in API version 64.0 and later.

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

## Special Access Rules

You need the Revenue Cloud Billing license, and the Payment Admin permission set or the
Payment Operations User permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| Description | Type  textarea  Properties  Create, Filter, Nillable, Sort, Update  Description  The user-entered description of the payment schedule treatment. |
| DueDateWindow | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The number that indicates the due date window of the payment schedule treatment. Available in API version 67.0 and later.  This field is a calculated field. |
| GroupingSource | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Specifies how the payment schedule treatments are grouped, such as by an invoice or account. Available in API version 67.0 and later.  Valid values are:  - `Invoice` - `Account` |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed this record or list view. If this value is null, and LastReferenceDate is not null, the user accessed this record or list view indirectly. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  Required. The user-entered name of the payment schedule treatment. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Required. The ID of the owner of the PaymentScheduleTreatment record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| PaymentSchedulePolicyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the related payment schedule policy.  This field is a relationship field.  Relationship Name  PaymentSchedulePolicy  Refers To  PaymentSchedulePolicy |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. The status of the payment schedule treatment.  Valid values are:  - `Active` - `Canceled` - `Draft` - `Inactive` |
| TriggerSource | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. The action that caused the payment schedule treatment to be created.  Valid value is:  - `InvoicePosted` |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[PaymentScheduleTreatmentShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
