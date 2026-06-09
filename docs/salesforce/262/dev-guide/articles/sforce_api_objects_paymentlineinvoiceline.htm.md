---
page_id: sforce_api_objects_paymentlineinvoiceline.htm
title: PaymentLineInvoiceLine
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_paymentlineinvoiceline.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# PaymentLineInvoiceLine

Represents information about a payment line that's applied to or
unapplied from an invoice line. This object is available in API version 64.0 and
later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`create()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`update()`,
`upsert()`

## Special Access Rules

You need the Revenue Cloud Billing license, and the Payment Admin permission set or the Payment
Operations User permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| AccountId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort  Description  The account of the customer who made a payment that's related to the payment line invoice line.  This field is a relationship field.  Relationship Name  Account  Refers To  Account |
| Amount | Type  currency  Properties  Create, Filter, Sort  Description  Required. The amount that's been applied or unapplied by a payment line. |
| AppliedDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort  Description  The date and time when a payment line was applied to an invoice line. |
| AppliedImpactAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  If the payment line invoice line's Type value is `Applied`, the applied impact amount is the same as the ImpactAmount value. The applied impact amount is 0 when the Type value is `Unapplied`.  This field is a calculated field. |
| Description | Type  textarea  Properties  Create, Filter, Nillable, Sort, Update  Description  Additional details about the payment line invoice line. |
| EffectiveDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort  Description  The date and time when a payment line's application to or unapplication from an invoice line becomes effective. |
| ImpactAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  If the payment line invoice line's Type value is `Applied`, the impact amount is the negative equivalent of the payment line invoice line's Amount value. Otherwise, it's equal to the payment line invoice line's Amount value.  This field is a calculated field. |
| InvoiceLineBalance | Type  currency  Properties  Filter, Nillable, Sort  Description  The balance of the invoice line after a payment line was applied to it or unapplied from it. |
| InvoiceLineId | Type  reference  Properties  Create, Filter, Group, Sort  Description  Required. The invoice line to which a payment line has been applied or unapplied.  This field is a relationship field.  Relationship Name  InvoiceLine  Relationship Type  Master-detail  Refers To  InvoiceLine (the master object) |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed this record or list view. If this value is null, and LastReferenceDate is not null, the user accessed this record or list view indirectly. |
| LegalEntityAccountingPeriodId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The legal entity accounting period related to the payment line invoice line.  This field is a relationship field.  Relationship Name  LegalEntityAccountingPeriod  Refers To  LegalEntyAccountingPeriod |
| LegalEntityId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The legal entity related to the payment line invoice line.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |
| PaymentBalance | Type  currency  Properties  Filter, Nillable, Sort  Description  The balance of the Payment record after it was applied to or unapplied from an invoice line. |
| PaymentId | Type  reference  Properties  Create, Filter, Group, Sort  Description  Required. The parent Payment record that's related to the payment line invoice line.  This field is a relationship field.  Relationship Name  Payment  Refers To  Payment |
| PaymentLineInvoiceLineNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. An auto-generated number identifying the payment line invoice line. |
| RelatedPaymentLineInvcLineId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort  Description  The related payment line invoice line with the Type value as `Applied` when the payment line invoice line's Type value is `Unapplied`.  This field is a relationship field.  Relationship Name  RelatedPaymentLineInvcLine  Refers To  PaymentLineInvoiceLine |
| Type | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort  Description  Required. Specifies whether a payment line has been applied to or unapplied from an invoice line.  Valid values are:  - `Applied` - `Unapplied` |
| UnappliedDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort  Description  The date and time when a payment line was unapplied from an invoice line. |
| UnappliedStatus | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort  Description  Required. Specifies whether a payment line has been unapplied from an invoice line.  Valid values are:  - `NA`—Not   Applicable - `No` - `Yes` |
