---
page_id: sforce_api_objects_creditmemoinvapplication.htm
title: CreditMemoInvApplication
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_creditmemoinvapplication.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# CreditMemoInvApplication

Represents information about the application of a credit memo to an
invoice. This object is available in API version 62.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`search()`,
`update()`

## Special Access Rules

You need the Credit Memo Operations User permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| Amount | Type  currency  Properties  Filter, Sort  Description  Required. The amount of the credit memo that was applied to or unapplied from the invoice. |
| AppliedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date when the credit memo was applied. If the credit memo invoice application's type is `Unapplied`, this value is inherited from the `Applied` date of the credit memo referenced in the AssociatedLineId field. |
| AssociatedLineId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  ID of the original credit memo invoice application for a credit memo invoice application that represents an unapplied credit memo.  This field is a relationship field.  Relationship Name  AssociatedLine  Refers To  CreditMemoInvApplication |
| CreditMemoBalance | Type  currency  Properties  Filter, Nillable, Sort  Description  The balance of a credit memo after it's applied or unapplied. This field is a snapshot of the credit memo's balance after the action. This field isn't updated after further changes to the credit memo balance. |
| CreditMemoId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The credit memo that was applied or unapplied.  This field is a relationship field.  Relationship Name  CreditMemo  Refers To  CreditMemo |
| CreditMemoInvoiceNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. An auto-generated number identifying the credit memo invoice application. |
| Date | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date when the credit memo amount was applied to the invoice. |
| Description | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  Additional details about the credit memo applied to an invoice. |
| EffectiveDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The effective date of the application or unapplication of credit. You can provide this value when applying or unapplying the credit memo. This field is optional and provided only for reporting purposes. It doesn't affect the credit memo invoice application's other fields. |
| HasBeenUnapplied | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Specifies whether this credit memo application has been unapplied from the target invoice.  Valid values are:  - `NA` - `No` - `Yes` |
| ImpactAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The net adjustment to the invoice's balance after a credit memo is applied or unapplied. If a credit memo was applied, this value is the negative version of the credit memo invoice application's Amount field. If a credit memo was unapplied, this value is the positive version of the credit memo invoice application's Amount field.  This field is a calculated field. |
| InvoiceBalance | Type  currency  Properties  Filter, Nillable, Sort  Description  The balance of the credit memo after a credit memo is applied or unapplied. This field is a snapshot of the credit memo's balance after the action. This field isn't updated after further changes to the credit memo balance. |
| InvoiceId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The invoice to which the credit memo is applied.  This field is a relationship field.  Relationship Name  Invoice  Relationship Type  Master-detail  Refers To  Invoice (the master object) |
| LegalEntityAccountingPeriodId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The legal entity accounting period record that’s related to the credit memo invoice application. This field is available in API version 67.0 and later.  This field is a relationship field.  Relationship Name  LegalEntityAccountingPeriod  Refers To  LegalEntyAccountingPeriod |
| LegalEntityId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The legal entity record that’s related to the credit memo invoice application. This field is available in API version 67.0 and later.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |
| Type | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. Specifies whether the credit memo line application was generated because of an apply action (application) or an unapply action (unapplication).  Valid values are:  - `Applied` - `Unapplied` |
| UnappliedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date when this application was unapplied from the target invoice. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[CreditMemoInvApplicationFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[CreditMemoInvApplicationHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.
