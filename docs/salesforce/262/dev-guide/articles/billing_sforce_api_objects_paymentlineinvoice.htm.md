---
page_id: billing_sforce_api_objects_paymentlineinvoice.htm
title: Billing Fields on PaymentLineInvoice
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_paymentlineinvoice.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_extended_standard_object_fields.htm
fetched_at: 2026-06-09
---

# Billing Fields on PaymentLineInvoice

Standard fields extend the PaymentLineInvoice object for use in
Billing to represent information about legal entities and legal entity accounting
periods. This object is available in API version 64.0 and later.

## Supported Calls

`create()`, `describeLayout()`, `describeSObjects()`,
`getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Special Access Rules

You need the Revenue Cloud Billing license, and the Payment Admin permission set or the
Payment Operations User permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| LegalEntityAccountingPeriodId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The legal entity accounting period related to the payment line invoice.  This field is a relationship field.  Relationship Name  LegalEntityAccountingPeriod  Refers To  LegalEntyAccountingPeriod |
| LegalEntityId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The legal entity related to the payment line invoice.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |

#### See Also

- [*Object Reference for the Salesforce Platform*: PaymentLineInvoice](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_paymentlineinvoice.htm "Object Reference for the Salesforce Platform: PaymentLineInvoice - HTML (New Window)")
