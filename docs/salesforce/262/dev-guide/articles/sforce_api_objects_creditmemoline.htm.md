---
page_id: sforce_api_objects_creditmemoline.htm
title: CreditMemoLine
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_creditmemoline.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# CreditMemoLine

Represents the product, service, adjustment, or tax line items
included in a credit memo. This object is available in API version 62.0 and
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

You need the Credit Memo Operations User permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| AdjustmentAmount | Type  currency  Properties  Filter, Nillable, Sort, Update  Description  The amount of this credit memo line item if its type is Adjustment. |
| AdjustmentAmountWithTax | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of the adjustment amount and the adjustment tax amount. Available in API versions 62.0 and 63.0. |
| AdjustmentTaxAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The amount of the tax related to the adjustment amount. Available in API versions 62.0 and 63.0. |
| Balance | Type  currency  Properties  Filter, Nillable, Sort  Description  The amount of the credit memo line available for allocation. |
| BillingAddressId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the billing address related to this credit memo line.  This field is a relationship field.  Relationship Name  BillingAddress  Refers To  CreditMemoAddressGroup |
| ChargeAmount | Type  currency  Properties  Filter, Nillable, Sort, Update  Description  The amount of this credit memo line item if its type is Charge. |
| ChargeAmountWithTax | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of the charge amount and the charge tax amount. Available in API versions 62.0 and 63.0. |
| ChargeTaxAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The amount of the tax related to the charge amount. Available in API versions 62.0 and 63.0. |
| CorpCurrencyCnvChargeAmt | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The amount of the credit memo line item if its type is `Charge` in corporate currency. Available in API version 63.0 and later. |
| CorpCurrencyCnvTotalTaxAmt | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The sum of the total amount with the tax on the credit memo line in corporate currency. Available in API version 63.0 and later. |
| CorporateCurrencyCvsnDate | Type  date  Properties  Filter, Group, Nillable, Sort, Update  Description  The date on which the credit memo line amounts are converted to the corporate currency. Available in API version 63.0 and later. |
| CorporateCurrencyCvsnRate | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The exchange rate that's used to convert the credit memo line amounts to the corporate currency. Available in API version 63.0 and later. |
| CorporateCurrencyIsoCode | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The currency ISO code of the corporate currency. Available in API version 63.0 and later. |
| CreditMemoId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The ID of the parent credit memo.  This field is a relationship field.  Relationship Name  CreditMemo  Relationship Type  Master-detail  Refers To  CreditMemo (the master object) |
| Description | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  Additional details about the credit memo line. |
| EndDate | Type  date  Properties  Filter, Group, Nillable, Sort, Update  Description  The description of the credit memo line. |
| FuncCrcyCnvTotalTaxAmount | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The total tax amount value in functional currency. Available in API version 66.0 and later. |
| FuncCurrencyCnvChargeAmt | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The charge amount value in functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyCvsnDate | Type  date  Properties  Filter, Group, Nillable, Sort, Update  Description  The date on which the credit memo line amounts are converted into functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyCvsnRate | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The exchange rate that's used to convert credit memo line amounts into functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyIsoCode | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The ISO code of the functional currency. Available in API version 66.0 and later. |
| LegalEntityAccountingPeriodId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The ID of the legal entity accounting period record of the credit memo line.  This field is a relationship field.  Relationship Name  LegalEntityAccountingPeriod  Refers To  LegalEntyAccountingPeriod |
| LegalEntityId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The ID of the legal entity record related to the credit memo line.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |
| LineAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The amount of the credit memo line.  This field is a calculated field. |
| Name | Type  string  Properties  Filter, Group, idLookup, Sort, Update  Description  Required. The name of the credit memo line. |
| NetCreditsApplied | Type  currency  Properties  Filter, Nillable, Sort  Description  The total amount applied to invoice lines from the credit memo. This amount is calculated by subtracting the total unapplied credit amount from the total applied credit amount.  This field is a calculated field. |
| Product2Id | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The ID of the product or service being credited in the credit memo line.  This field is a relationship field.  Relationship Name  Product2  Refers To  Product2 |
| ReferenceEntityItemId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The order product or invoice line corresponding to this credit memo line.  This field is a polymorphic relationship field.  Relationship Name  ReferenceEntityItem  Refers To  InvoiceLine, OrderItem |
| ReferenceEntityItemType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The type of transaction that generated the credit memo line.  Valid values are:  - `Delivery Charge` - `Fee` - `Order Product` |
| ReferenceEntityItemTypeCode | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The type of object that generated the credit memo line.  Valid values are:  - `Charge` - `Product` |
| ShipFromAddressId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The address from which the product in the credit memo line is shipped. Available in API version 64.0 and later.  This field is a relationship field.  Relationship Name  ShipFromAddress  Refers To  CreditMemoAddressGroup |
| ShippingAddressId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the shipping address.  This field is a relationship field.  Relationship Name  ShippingAddress  Refers To  CreditMemoAddressGroup |
| StartDate | Type  date  Properties  Filter, Group, Nillable, Sort, Update  Description  The first date of the billing for the service for credit memo lines generated from a time-based service. |
| Status | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The status of the credit memo line. This field is inherited from the credit memo. |
| TaxAmount | Type  currency  Properties  Filter, Nillable, Sort, Update  Description  The total tax amount for the credit memo. |
| TaxTreatmentId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the tax treatment record for the credit memo line.  This field is a relationship field.  Relationship Name  TaxTreatment  Refers To  TaxTreatment |
