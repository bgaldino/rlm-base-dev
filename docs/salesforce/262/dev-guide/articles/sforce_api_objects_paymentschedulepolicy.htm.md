---
page_id: sforce_api_objects_paymentschedulepolicy.htm
title: PaymentSchedulePolicy
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_paymentschedulepolicy.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# PaymentSchedulePolicy

Represents information about the configuration for the payment schedule.
This object is available in API version 64.0 and later.

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
| DefaultTreatmentId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The default payment schedule treatment.  This field is a relationship field.  Relationship Name  DefaultTreatment  Refers To  PaymentScheduleTreatment |
| Description | Type  textarea  Properties  Create, Filter, Nillable, Sort, Update  Description  The user-entered description for the payment schedule policy. |
| IsOrgDefault | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  If the payment schedule policy is the default policy for the org, this value is set to `true`. If not, this value is set to `false`. An org can have only one default payment policy.  The default value is `false`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed this record or list view. If this value is null, and LastReferenceDate is not null, the user accessed this record or list view indirectly. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The user-entered name of the payment schedule policy. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Required. The ID of the owner of the PaymentSchedulePolicy record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The status of the payment schedule policy.  Valid values are:  - `Active` - `Canceled` - `Draft` - `Inactive` |
| TreatmentSelection | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Specifies the payment schedule treatment.  Valid value is:  - `Default`—Uses the   payment schedule treatment indicated by the   DefaultTreatmentId field. |
