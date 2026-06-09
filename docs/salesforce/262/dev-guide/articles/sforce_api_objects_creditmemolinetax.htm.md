---
page_id: sforce_api_objects_creditmemolinetax.htm
title: CreditMemoLineTax
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_creditmemolinetax.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# CreditMemoLineTax

Represents tax information of a credit memo line of type `Tax`. This object is available in API version 62.0 and
later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`,
`getUpdated()`, `query()`, `retrieve()`, `search()`, `update()`

## Special Access Rules

You need the Tax Admin permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| BillingAddressId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The billing address of the parent credit memo line.  This field is a relationship field.  Relationship Name  BillingAddress  Refers To  CreditMemoAddressGroup |
| CalculationStatus | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  The status of the tax calculation.  Valid values are:  - `Complete` - `Error` - `None`  The default value is `None`. |
| CorpCrcyCnvTaxAmount | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The total tax amount of the credit memo line tax in corporate currency. Available in API version 63.0 and later. |
| CorporateCurrencyCvsnDate | Type  date  Properties  Filter, Group, Nillable, Sort, Update  Description  The date on which the credit memo line tax amounts are converted to the corporate currency. Available in API version 63.0 and later. |
| CorporateCurrencyCvsnRate | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The exchange rate that's used to convert the credit memo line tax amounts to the corporate currency. Available in API version 63.0 and later. |
| CorporateCurrencyIsoCode | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The currency ISO code of the corporate currency. Available in API version 63.0 and later. |
| CreditMemoLineId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The ID of the parent charge or adjustment credit memo line record that a credit memo line tax is related to.  This field is a relationship field.  Relationship Name  CreditMemoLine  Relationship Type  Master-detail  Refers To  CreditMemoLine (the master object) |
| CreditMemoLineTaxNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. An auto-generated number identifying a credit memo line tax. |
| Description | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  Additional details about the credit memo line tax. |
| EndDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The end date of a credit memo line tax. |
| FuncCrcyCnvTaxAmount | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The tax amount value in functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyCvsnDate | Type  date  Properties  Filter, Group, Nillable, Sort, Update  Description  The date on which the tax amount value is converted into functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyCvsnRate | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The exchange rate that's used to convert the tax amount value into functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyIsoCode | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The ISO code of the functional currency. Available in API version 66.0 and later. |
| LegalEntityAccountingPeriodId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the legal entity accounting period record that's related to a credit memo line tax.  This field is a relationship field.  Relationship Name  LegalEntityAccountingPeriod  Refers To  LegalEntyAccountingPeriod |
| LegalEntityId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The ID of the legal entity record that's related to a credit memo line tax.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |
| Product2Id | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The product or service being credited in the parent credit memo line. Available in API version 62.0 only.  This field is a relationship field.  Relationship Name  Product2  Refers To  Product2 |
| ReferenceEntityItemId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The invoice line tax corresponding to a credit memo line tax.  This field is a relationship field.  Relationship Name  ReferenceEntityItem  Refers To  InvoiceLineTax |
| ShipFromAddressId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ship from address specified in the parent credit memo line. Available in API version 64.0 and later.  This field is a relationship field.  Relationship Name  ShipFromAddress  Refers To  CreditMemoAddressGroup |
| ShippingAddressId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The shipping address of the parent credit memo line.  This field is a relationship field.  Relationship Name  ShippingAddress  Refers To  CreditMemoAddressGroup |
| StartDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The start date of a credit memo line tax. |
| TaxAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The total amount of a credit memo line tax. |
| TaxCode | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The code that's used to calculate the tax rate for the parent credit memo line. |
| TaxDocumentNumber | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The document number that's used to calculate the tax rate for the parent credit memo line. |
| TaxEffectiveDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The date used to calculate the tax amount. |
| TaxName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The user-defined name for a credit memo line tax. |
| TaxRate | Type  percent  Properties  Filter, Nillable, Sort  Description  The percentage that's used to calculate tax. |
| TaxTransactionNumber | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The number of the transaction in the external tax engine that calculated tax for the parent credit memo line. |
| TaxTreatmentId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the tax treatment record that's related to a credit memo line tax.  This field is a relationship field.  Relationship Name  TaxTreatment  Refers To  TaxTreatment |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[CreditMemoLineTaxFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[CreditMemoLineTaxHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.
