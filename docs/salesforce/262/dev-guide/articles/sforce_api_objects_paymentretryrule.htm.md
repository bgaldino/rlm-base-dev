---
page_id: sforce_api_objects_paymentretryrule.htm
title: PaymentRetryRule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_paymentretryrule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# PaymentRetryRule

Represents the specific payment retry rule for a failed payment
schedule item. Each rule defines actionable parameters such as the maximum number of
retries for the failed records and time intervals between subsequent retry attempts.
This object is available in API version 66.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| Description | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The description of the business details for the payment retry rule. |
| IntervalUnit | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The unit of time after which a payment batch run must retry the failed payments.  Valid values are:  - `Days` - `Hours` - `Minutes` |
| IntervalValue | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The single or comma-separated numeric values, after which the payment batch run must retry the failed payments. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed the payment retry rule record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed the payment retry rule record. |
| MaximumRetryCount | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The maximum number of retries on the failed payment records. |
| PaymentGatewayErrorCategory | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The category of payment gateway errors for which the payment retry rule must be applied.  Valid values are:  - `CardLimit`—Card   Limit Decline - `GatewayConnection`—Gateway Connection   Error - `PaymentInformation`—Invalid Payment   Details - `PaymentProcessing`—Payment Processing   Error - `Security`—Security Failure - `Unknown`—Unknown   Error - `ValidationFailure`—Internal Validation   Error |
| PaymentGatewayErrorCode | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The raw error code of the payment gateway response. |
| PaymentGatewayId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The unique identifier of the payment gateway for which the payment retry rule must be applied.  This field is a relationship field.  Relationship Name  PaymentGateway  Refers To  PaymentGateway |
| PaymentRetryRuleSetId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The payment retry rule set of the payment retry rule.  This field is a relationship field.  Relationship Name  PaymentRetryRuleSet  Relationship Type  Master-detail  Refers To  PaymentRetryRuleSet (the master object) |
| RetryIntervalType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies whether the payment retry rule must be applied to the failed payment records at fixed or staggered intervals of time.  Valid values are:  - `Fixed` - `Staggered` |
