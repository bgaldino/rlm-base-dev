---
page_id: sforce_api_objects_debitmemoline.htm
title: DebitMemoLine
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_debitmemoline.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# DebitMemoLine

Represents the additional charge amount that the buyer must pay for
the product, service, or debit memo line tax that’s related to the debit memo. This
object is available in API version 65.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms
to align with our company value of Equality. We maintained certain terms to avoid any
effect on customer implementations.

## Supported Calls

`create()`, `describeLayout()`, `describeSObjects()`,
`getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `update()`, `upsert()`

## Special Access Rules

You need Revenue Cloud Billing license and one of these permission sets to access this
object.

- Billing Admin permission set
- Billing Operations User permission set
- Payments Admin permission set
- Payments Operation User permission set
- Credit Memo Operations User permission set

## Fields

| Field | Details |
| --- | --- |
| BillingAddressId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The billing address record that’s related to the debit memo line.  This field is a relationship field.  Relationship Name  BillingAddress  Refers To  DebitMemoAddress |
| ChargeAmount | Type  currency  Properties  Create, Filter, Sort, Update  Description  The amount of the debit memo line item. |
| CorpCurrencyCnvChargeAmt | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The charge amount of the debit memo line in corporate currency. |
| CorporateCurrencyCvsnDate | Type  date  Properties  Filter, Group, Nillable, Sort, Update  Description  The date on which the debit memo line amounts are converted into corporate currency. |
| CorporateCurrencyCvsnRate | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The exchange rate that’s used to convert debit memo line amounts into corporate currency. |
| CorporateCurrencyIsoCode | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The currency ISO code of the corporate currency. |
| DebitMemoId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The parent debit memo record that’s related to the debit memo line record.  This field is a relationship field.  Relationship Name  DebitMemo  Relationship Type  Master-detail  Refers To  DebitMemo (the master object) |
| Description | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The description of the debit memo line. |
| EndDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The end date of the debit memo line that determines which billing cycle it must be associated with. |
| FuncCrcyCnvTotalTaxAmt | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The total tax amount value in functional currency. Available in API version 66.0 and later. |
| FuncCrcyCnvChargeAmount | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The charge amount value in functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyCvsnDate | Type  date  Properties  Filter, Group, Nillable, Sort, Update  Description  The date on which the debit memo line amounts is converted into functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyCvsnRate | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The exchange rate that's used to convert the debit memo line amounts into functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyIsoCode | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The ISO code of the functional currency. Available in API version 66.0 and later. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed a debit memo address record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed a debit memo address record. If this value is null, it’s possible that the user only accessed the debit memo address record or a related list view (LastReferencedDate), but not viewed the debit memo address record itself. |
| LegalEntityAccountingPeriodId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The legal entity accounting period record that’s related to the debit memo line.  This field is a relationship field.  Relationship Name  LegalEntityAccountingPeriod  Refers To  LegalEntyAccountingPeriod |
| LegalEntityId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The legal entity record that’s related to the debit memo line.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  An auto-generated name assigned to the debit memo line. |
| Product2Id | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the product or service being debited in the debit memo line.  This field is a relationship field.  Relationship Name  Product2  Refers To  Product2 |
| ReferenceRecordId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The record ID associated with the debit memo line record. The record ID is an asset, invoice line, contract, or refund record.  This field is a polymorphic relationship field.  Relationship Name  ReferenceRecord  Refers To  Asset, Contract, InvoiceLine, Refund, Credit Memo Line |
| ShippingAddressId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The shipping address record that’s related to the debit memo line.  This field is a relationship field.  Relationship Name  ShippingAddress  Refers To  DebitMemoAddress |
| StartDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The start date of the debit memo line that determines which billing cycle it must be associated with. |
| TaxTreatmentId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the tax treatment record that’s related to the debit memo line.  This field is a relationship field.  Relationship Name  TaxTreatment  Refers To  TaxTreatment |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[DebitMemoLineFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[DebitMemoLineHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.
