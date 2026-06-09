---
page_id: sforce_api_objects_invoiceline.htm
title: InvoiceLine
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_invoiceline.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# InvoiceLine

Represents the amount that a buyer must pay for a product, service,
or fee. Invoice lines are created based on the amount of an order line. This object is
available in API version 62.0 and later.

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

You need the Billing Admin permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| AdjustmentAmount | Type  currency  Properties  Filter, Nillable, Sort, Update  Description  The sum of adjustments made to the invoice line. |
| AdjustmentAmountWithTax | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of adjustment amounts, including associated taxes related to the invoice line. |
| AdjustmentTaxAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The sum of tax adjustments to the invoice line. |
| Balance | Type  currency  Properties  Filter, Nillable, Sort  Description  The outstanding balance for an invoice line. This amount is equal to the invoice’s total amount with tax after deducting the payments made. |
| BillingAddressId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  This field is related to an InvoiceAddressGroup field containing the billing address for the invoice line. For example, one InvoiceAddressGroup field is related to the invoiceLine's BillingAddressID field, and another InvoiceAddressGroup field is related to the invoiceLine's ShippingAddressId field.  This field is a relationship field.  Relationship Name  BillingAddress  Refers To  InvoiceAddressGroup |
| BillingScheduleGroupId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The ID of the billing schedule group for the invoice line.  This field is a relationship field.  Relationship Name  BillingScheduleGroup  Refers To  BillingScheduleGroup |
| BillingScheduleId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The ID of the billing schedule for the invoice line. Edit access is enabled for this field. You must not modify this field when the invoice line is related to a posted invoice.  This field is a relationship field.  Relationship Name  BillingSchedule  Refers To  BillingSchedule |
| ChargeAmount | Type  currency  Properties  Filter, Nillable, Sort, Update  Description  The sum of charges made to the invoice line. |
| ChargeAmountWithTax | Type  currency  Properties  Filter, Nillable, Sort  Description  The amount on a charge invoice line, including tax. |
| ChargeConvertedNegAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The amount on a charge invoice line that’s converted to credit. |
| ChargeTaxAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The tax to be applied on a charge invoice line. |
| ConvertedNegAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The amount from an invoice line that’s converted to credit. |
| CorpCurrencyCnvChargeAmt | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The sum of charges made to the invoice line in corporate currency. Available in API version 63.0 and later. |
| CorpCurrencyCnvTotalTaxAmt | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The total tax amount of the invoice line in corporate currency. Available in API version 63.0 and later. |
| CorporateCurrencyCvsnDate | Type  date  Properties  Filter, Group, Nillable, Sort, Update  Description  The date on which the invoice line amounts are converted to corporate currency. Available in API version 63.0 and later. |
| CorporateCurrencyCvsnRate | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The exchange rate that's used to convert the invoice line amounts to corporate currency. Available in API version 63.0 and later. |
| CorporateCurrencyIsoCode | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The currency ISO code of the corporate currency. Available in API version 63.0 and later. |
| Description | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The description of the invoice line. |
| FuncCrcyCnvTotalTaxAmt | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The total tax amount value in functional currency. Available in API version 66.0 and later. |
| FuncCurrencyCnvChargeAmt | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The charge amount value in functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyCvsnDate | Type  date  Properties  Filter, Group, Nillable, Sort, Update  Description  The date on which the invoice line amount values are converted into functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyCvsnRate | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The exchange rate that's used to convert the invoice line amount values into functional currency. Available in API version 66.0 and later. |
| FunctionalCurrencyIsoCode | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The ISO code of the functional currency. Available in API version 66.0 and later. |
| GroupReferenceEntityItemId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The ID of the record that the invoice line corresponds to.  This field is a polymorphic relationship field.  Relationship Name  GroupReferenceEntityItem  Refers To  DebitMemoLine, OrderItem, OrderItemAdjustmentLineItem, OrderItemDetail, QuoteLineDetail, QuoteLineItem |
| HasMultipleItems | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Required. Indicates whether this field merges items from the same billing period (`true`) or not (`false`).  The default value is `false`. |
| InvoiceId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The ID of the invoice record that contains this invoice line.  This field is a relationship field.  Relationship Name  Invoice  Relationship Type  Master-detail  Refers To  Invoice (the master object) |
| InvoiceLineEndDate | Type  date  Properties  Filter, Group, Sort, Update  Description  Required. The end date of the billing for the service for invoice lines made from a time-based service. |
| InvoiceLineStartDate | Type  date  Properties  Filter, Group, Sort, Update  Description  Required. The first date of the billing for the service for invoice lines made from a time-based service. |
| InvoiceStatus | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The status of the invoice line. This field is inherited from the invoice’s status. |
| IsUsageBasedInvoiceLine | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Required. Indicates whether the product is usage-based (`true`) or not (`false`).  The default value is `false`. This field is available in API version 63.0 and later with Revenue Cloud Billing license. |
| LegalEntityAccountingPeriodId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The ID of the legal entity accounting period record used in this invoice line.  This field is a relationship field.  Relationship Name  LegalEntityAccountingPeriod  Refers To  LegalEntyAccountingPeriod |
| LegalEntityId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The ID of the legal entity record used in this invoice line.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |
| LineAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The amount of the invoice line.  This field is a calculated field. |
| Name | Type  string  Properties  Filter, Group, idLookup, Sort, Update  Description  Required. The name of the invoice line. |
| NetCreditsApplied | Type  currency  Properties  Filter, Nillable, Sort  Description  The total credit memo line amount applied to the invoice line. This amount is calculated by subtracting the unapplied credit memo line amount from the applied credit memo line amount.  This field is a calculated field. |
| NetPaymentsApplied | Type  currency  Properties  Filter, Nillable, Sort  Description  The total payment amount that’s applied to the invoice line after unapplication of payments. This amount is calculated by subtracting the unapplied payment line invoice line amount from the applied payment line invoice line amount. Available in API version 61.0 and later.  This field is a calculated field. |
| OverageUnitOfMeasure | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The unit that’s used to measure the overage. For example, byte or minute. This field is available in API version 63.0 and later with Revenue Cloud Billing license. |
| ParentInvoiceLineId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the parent invoice line record.  This field is a relationship field.  Relationship Name  ParentInvoiceLine  Refers To  InvoiceLine |
| Product2Id | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The ID of the product that was charged or ordered to create the invoice line.  This field is a relationship field.  Relationship Name  Product2  Refers To  Product2 |
| Quantity | Type  double  Properties  Filter, Nillable, Sort, Update  Description  The number of units of the order product that created the invoice line. |
| ReferenceEntityItemId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The order item or adjustment item that created the invoice line.  This field is a polymorphic relationship field.  Relationship Name  ReferenceEntityItem  Refers To  OrderItem, OrderItemAdjustmentLineItem |
| ReferenceEntityItemType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The type of transaction that created the invoice line.  Valid values are:  - `Delivery Charge` - `Fee` - `Order Product` |
| ReferenceEntityItemTypeCode | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The type of object that created the invoice line.  Valid values are:  - `Charge` - `Product` |
| ShipFromAddressId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The shipping origin of the invoiced product. Available in API version 64.0 and later.  This field is a relationship field.  Relationship Name  ShipFromAddress  Refers To  InvoiceAddressGroup |
| ShippingAddressId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the shipping address record associated with the invoice line.  This field is a relationship field.  Relationship Name  ShippingAddress  Refers To  InvoiceAddressGroup |
| TaxAmount | Type  currency  Properties  Filter, Nillable, Sort, Update  Description  The total tax for the invoice line. |
| TaxProcessingStatus | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The status of the tax processing of the invoice line.  Valid values are:  - `Estimated` - `Pending` - `Posted` |
| TaxTreatmentId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The tax treatment used on this invoice line.  This field is a relationship field.  Relationship Name  TaxTreatment  Refers To  TaxTreatment |
| Type | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  The type of the invoice line.  Valid values are:  - `Adjustment` - `Charge` - `Tax` |
| UnitOfMeasureId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The unit of measure of the product associated with the invoice line. Available in API version 63.0 and later.  This field is a relationship field.  Relationship Name  UnitOfMeasure  Refers To  UnitOfMeasure |
| UnitPrice | Type  currency  Properties  Filter, Nillable, Sort, Update  Description  The price for one unit of the item on the invoice line. |
| UsageOverageQuantity | Type  double  Properties  Filter, Nillable, Sort  Description  The quantity of the usage overage that’s being invoiced. This field is available in API version 63.0 and later with Revenue Cloud Billing license. |
| UsageProductBillSchdGrpId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the usage-based product billing schedule group associated with the invoice line. This field is available in API version 63.0 and later with Revenue Cloud Billing license.  This field is a relationship field.  Relationship Name  UsageProductBillSchdGrp  Refers To  BillingScheduleGroup |
| UsageProductId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the usage-based product that was charged or ordered to create the invoice line. This field is available in API version 63.0 and later with Revenue Cloud Billing license.  This field is a relationship field.  Relationship Name  UsageProduct  Refers To  Product2 |
