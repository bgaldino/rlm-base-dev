---
page_id: sforce_api_objects_paymentscheduletreatmentdtl.htm
title: PaymentScheduleTreatmentDtl
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_paymentscheduletreatmentdtl.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# PaymentScheduleTreatmentDtl

Represents information about the processing of payment schedules after the
corresponding invoices are posted. This object is available in API version 64.0 and
later.

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
| DateOffset | Type  int  Properties  Create, Filter, Group, Sort, Update  Description  Required. The date offset is subtracted from the ProcessingDateReference value to determine the processing date. It must be a number equal to or less than 0. For example, if the invoice due date is 10/17/2025 and the date offset is -7, the payment schedule item is processed by jobs that run on or before 10/10/2025. |
| Description | Type  textarea  Properties  Create, Filter, Nillable, Sort, Update  Description  The user-entered description for the payment schedule treatment detail. |
| InstallmentPaymentType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. Indicates how the payment amount is divided into multiple payments.  Valid value is:  - `Percentage` |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed this record or list view. If this value is null, and LastReferenceDate is not null, the user accessed this record or list view indirectly. |
| PaymentMethodSelectionType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. Indicates how the payment method is specified.  Valid values are:  - `Manual`—The user   enters the payment method. - `MostRecentAutopay`—The payment method is the   most recently used automatic payment method. - `DefaultSavedPaymentMethod`—The default   payment method used for processing payments. Available in API   version 65.0 and later. |
| PaymentRunMatchingValue | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The value for the condition specified for the payment run criteria. When a payment batch run starts, all the payment schedule items that meet the specified criteria are processed. |
| PaymentScheduleTreatmentDetailNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. The system-generated unique identifier for the payment schedule treatment detail. |
| PaymentScheduleTreatmentId | Type  reference  Properties  Create, Filter, Group, Sort  Description  Required. The ID of the related payment schedule treatment.  This field is a relationship field.  Relationship Name  PaymentScheduleTreatment  Relationship Type  Master-detail  Refers To  PaymentScheduleTreatment (the master object) |
| Percentage | Type  percent  Properties  Create, Filter, Nillable, Sort, Update  Description  The percentage of the source amount that's used to create the payment schedule. |
| ProcessingDateReference | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. The source of the reference date.  Valid value is:  - `InvoiceDueDate` |
| PymtSchdDistributionMethodId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  Required. The distribution method that contains the information on how to create the payment schedule items.  This field is a relationship field.  Relationship Name  PymtSchdDistributionMethod  Refers To  PymtSchdDistributionMethod |
