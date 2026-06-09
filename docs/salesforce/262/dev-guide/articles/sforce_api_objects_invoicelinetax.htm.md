---
page_id: sforce_api_objects_invoicelinetax.htm
title: InvoiceLineTax
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_invoicelinetax.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# InvoiceLineTax

Represents tax information of an invoice line of type `Tax`. This object is available in API version 62.0 and
later.

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

You need the Tax Admin permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| BillingAddressId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The billing address of the parent invoice line. Edit access is enabled for this field. You must not modify this field when the invoice line is related to a posted invoice.  This field is a relationship field.  Relationship Name  BillingAddress  Refers To  InvoiceAddressGroup |
| ConvertedNegAmount | Type  currency  Properties  Filter, Nillable, Sort, Update  Description  The amount from the parent invoice line that's converted to credit. Edit access is enabled for this field. You must not modify this field when the invoice line is related to a posted invoice. |
| CorpCrcyCnvTaxAmount | Type  double  Properties  Filter, Group, Nillable, Sort  Description  The total tax amount of the invoice line tax in corporate currency. Available in API version 63.0 and later. |
| CorporateCurrencyCvsnDate | Type  date  Properties  Filter, Group, Nillable, Sort  Description  The date on which the invoice line tax amounts are converted to the corporate currency. Available in API version 63.0 and later. |
| CorporateCurrencyCvsnRate | Type  double  Properties  Filter, Nillable, Sort  Description  The exchange rate that's used to convert the invoice line tax amounts to the corporate currency. Available in API version 63.0 and later. |
| CorporateCurrencyIsoCode | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The currency ISO code of the corporate currency. Available in API version 63.0 and later. |
| Description | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  Additional details about the invoice line tax. |
| EndDate | Type  date  Properties  Filter, Group, Sort, Update  Description  Required. The end date of an invoice line tax. |
| FuncCrcyCnvTaxAmount | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The tax amount value in functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyCvsnDate | Type  date  Properties  Filter, Group, Nillable, Sort, Update  Description  The date on which the tax amount value is converted into functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyCvsnRate | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The exchange rate that's used to convert the tax amount value into functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyIsoCode | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The ISO code of the functional currency. Available in API version 66.0 and later. |
| InvoiceLineId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The ID of the parent charge or adjustment invoice line record that an invoice line tax is related to.  This field is a relationship field.  Relationship Name  InvoiceLine  Relationship Type  Master-detail  Refers To  InvoiceLine (the master object) |
| InvoiceLineTaxNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. An auto-generated number identifying an invoice line tax. |
| LegalEntityAccountingPeriodId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The ID of the legal entity accounting period record that's related to an invoice line tax.  This field is a relationship field.  Relationship Name  LegalEntityAccountingPeriod  Refers To  LegalEntyAccountingPeriod |
| LegalEntityId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The ID of the legal entity that's related to an invoice line tax.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |
| Product2Id | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The product that was charged or ordered to create the parent invoice line. Available in API version 62.0 only.  This field is a relationship field.  Relationship Name  Product2  Refers To  Product2 |
| Quantity | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The number of units of the order product that created the parent invoice line. Available in API version 62.0 only. |
| ShipFromAddressId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ship from address specified in the parent invoice line. Edit access is enabled for this field. You must not modify this field when the invoice line is related to a posted invoice. Available in API version 64.0 and later.  This field is a relationship field.  Relationship Name  ShipFromAddress  Refers To  InvoiceAddressGroup |
| ShippingAddressId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The ID of the shipping address record of the parent invoice line. Edit access is enabled for this field. You must not modify this field when the invoice line is related to a posted invoice.  This field is a relationship field.  Relationship Name  ShippingAddress  Refers To  InvoiceAddressGroup |
| StartDate | Type  date  Properties  Filter, Group, Sort, Update  Description  Required. The start date of an invoice line tax. |
| TaxAmount | Type  currency  Properties  Filter, Nillable, Sort, Update  Description  The total amount of an invoice line tax. Edit access is enabled for this field. You must not modify this field when the invoice line is related to a posted invoice. Available in API version 65.0 and later. |
| TaxCode | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The code that's used to calculate the tax rate for the parent invoice line. Edit access is enabled for this field. You must not modify this field when the invoice line is related to a posted invoice. |
| TaxDocumentNumber | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The number of the latest record in the external tax engine in which the parent invoice line is included. Edit access is enabled for this field. You must not modify this field when the invoice line is related to a posted invoice. |
| TaxEffectiveDate | Type  date  Properties  Filter, Group, Nillable, Sort, Update  Description  The date used to calculate the tax amount. Edit access is enabled for this field. You must not modify this field when the invoice line is related to a posted invoice. |
| TaxExemptAmount | Type  currency  Properties  Filter, Nillable, Sort, Update  Description  The amount that's exempted from tax. Edit access is enabled for this field. You must not modify this field when the invoice line is related to a posted invoice. |
| TaxName | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The user-defined name for an invoice line tax. Edit access is enabled for this field. You must not modify this field when the invoice line is related to a posted invoice. |
| TaxProcessingStatus | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The processing status of the invoice line tax.  Valid values are:  - `Estimated` - `Pending` - `Posted` |
| TaxRate | Type  percent  Properties  Filter, Nillable, Sort, Update  Description  The percentage of the order product price that's used to calculate tax. Edit access is enabled for this field. You must not modify this field when the invoice line is related to a posted invoice. |
| TaxTransactionNumber | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The number of the transaction in the external tax engine that calculated tax for the parent invoice line. |
| TaxTreatmentId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The ID of the tax treatment record that's related to an invoice line tax. Edit access is enabled for this field. You must not modify this field when the invoice line is related to a posted invoice.  This field is a relationship field.  Relationship Name  TaxTreatment  Refers To  TaxTreatment |
| UnitPrice | Type  currency  Properties  Filter, Nillable, Sort, Update  Description  The price per unit of the order product that's related to an invoice line tax. Available in API version 62.0 only. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[InvoiceLineTaxFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[InvoiceLineTaxHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.
