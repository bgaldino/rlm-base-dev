---
page_id: billing_tax_contract_mappings_for_invoices_and_credits.htm
title: Tax Mappings for Invoices and Credits
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_tax_contract_mappings_for_invoices_and_credits.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_tax_engine_adapter_interface_for_standard_tax.htm
fetched_at: 2026-06-09
---

# Tax Mappings for Invoices and Credits

You can extend and customize the existing tax interface by using custom metadata types
and tax mappings. These customizations help you with unique business requirements such as the
inclusion of specific data for accurate calculations and audits.

Here are some prerequisites before you work with the tax mappings for invoices and
credits.

- See [custom metadata types](https://help.salesforce.com/s/articleView?id=platform.custommetadatatypes_overview.htm&language=en_US "HTML (New Window)") to
  specify all your tax mapping definitions.
- See [details on extension of your tax
  contract](https://help.salesforce.com/s/articleView?id=ind.billing_custom_metadata_types_configure.htm&language=en_US "HTML (New Window)") with custom fields.
- Tax callout extensions are supported for the Invoice, Invoice Line, Invoice Line Tax,
  Credit Memo, Credit Memo Line, and Credit Memo Line Tax objects.

## Request Mappings for Header Attributes

This table defines the request mappings between the header attributes of a tax callout and
fields of applicable objects.

| Header Attributes | Invoice Mapping | Negative Invoice Mapping | Credit Mapping |
| --- | --- | --- | --- |
| currencyIsoCode | Invoice.CurrencyISOCode | Invoice.CurrencyISOCode | CreditMemo.CurrencyISOCode |
| isCommit | If status is `DRAFT` then this value is `False`. If status is `POSTED`, then this value is `True`. | If status is `DRAFT` then this value is `False`. If status is POSTED, then this value is `True`. | This value is `True` until Summer ’25. From Winter ’26, if status is `DRAFT`, then this value is `False`. If status is `POSTED`, then this value is `True`. |
| referenceEntityId | Invoice.ID | Invoice.ID | CreditMemo.ID |
| taxEngineId | TaxTreatment.TaxEngine.ID | TaxTreatment.TaxEngine.ID | TaxTreatment.TaxEngine.ID |
| transactionDate | SystemDate | SystemDate | SystemDate |
| **sellerDetails** |  |  |  |
| code | TaxEngine.SellerCode | TaxEngine.SellerCode | TaxEngine.SellerCode |
| **customerDetails** |  |  |  |
| accountId | Invoice.BillingAccount.ID | Invoice.BillingAccount.ID | CreditMemo.BillingAccount.ID |
| code | NULL | NULL | NULL |
| exemptionNo | Invoice.BillingAccount.TaxExemptionNumber. Available from Spring ’26. | Invoice.BillingAccount.TaxExemptionNumber Available from Spring ’26. | CreditMemo.BillingAccount.TaxExemptionNumber Available from Spring ’26. |
| exemptionReason | NULL | NULL | NULL |
| exemptionStatus | Invoice.BillingAccount.TaxExemptionStatus Available from Spring ’26. | Invoice.BillingAccount.TaxExemptionStatus Available from Spring ’26. | CreditMemo.BillingAccount.TaxExemptionStatus Available from Spring ’26. |
| exemptionExpirationDate | Invoice.BillingAccount.TaxExemptionExpirationDate Available from Spring ’26. | Invoice.BillingAccount.TaxExemptionExpirationDate Available from Spring ’26. | CreditMemo.BillingAccount.TaxExemptionExpirationDate Available from Spring ’26. |
| deliveryTerms | Invoice.BillingAccount.DeliveryTerms Available from Spring ’26. | Invoice.BillingAccount.DeliveryTerms Available from Spring ’26. | CreditMemo.BillingAccount.DeliveryTerms Available from Spring ’26. |
| billingProfileId | Invoice.BillingAccount.ID Available from Spring ’26. | Invoice.BillingAccount.ID Available from Spring ’26. | CreditMemo.BillingAccount.ID Available from Spring ’26. |
| additionalTaxIdentificationDetails | Invoice.BillingAccount.AddTaxIdentificationDetails Available from Spring ’26. | Invoice.BillingAccount.AddTaxIdentificationDetails Available from Spring ’26. | CreditMemo.BillingAccount.AddTaxIdentificationDetails Available from Spring ’26. |
| taxIdentificationNumber | Invoice.BillingAccount.TaxIdentificationNumber Available from Spring ’26. | Invoice.BillingAccount.TaxIdentificationNumber Available from Spring ’26. | CreditMemo.BillingAccount.TaxIdentificationNumber Available from Spring ’26. |
| taxType | If status is `DRAFT`, then this value is `Estimated`. If status is `POSTED`, then this value is `Actual`. | If status is `DRAFT`, then this value is `Estimated`. If status is `POSTED`, then this value is `Actual`. | This value is `Actual` until Summer ’25. From Winter ’26, if status is `DRAFT`, then this value is `Estimated`. If status is POSTED, then this value is `Actual`. |
| taxTransactionType | Debit | Credit | Credit |
| effectiveDate | invoice.InvoiceDate | If you're creating from negative lines, then this value is the original `Invoice.InvoiceDate` value. | If you're using standalone credit memo, then this value is the `CreditMemo.CreditDate` value. |
| **addresses** |  |  |  |
| billTo | NULL | NULL | NULL |
| shipTo | NULL | NULL | NULL |
| shipFrom | NULL | NULL | NULL |
| soldTo | NULL | NULL | NULL |
| taxEngineAddress | TaxEngine.Address | TaxEngine.Address | TaxEngine.Address |
| referenceDocumentCode | NULL | If you're converting from negative lines, then this value is the original document code `Invoice.ID & "Debit" & TaxEngine.ID`. | If you're using standalone credit memo, then this value is NULL. Otherwise, this value is the `documentCode` value of the original invoice. |
| description | Invoice.Description | Invoice.Description | Invoice.Description |
| documentCode | `Invoice.ID & "_Debit_" & TaxEngine.ID` | `Invoice.ID & "_Credit_" & TaxEngine.ID` | `CreditMemo.ID & "_Credit_" & TaxEngine.ID` |
| shouldVoid | FALSE | From Winter ’26, if the request is to void a posted invoice, then this value is TRUE. Else, it is FALSE. | FALSE |
| lineItems | Refer to the next line attributes section. | Refer to the next line attributes section. | Refer to the next line attributes section. |

## Request Mappings for Line Attributes

This table defines the request mappings between the line attributes of a tax callout and
fields of applicable objects.

| Line Attributes | Invoice Mapping | Negative Invoices | Credit Mapping |
| --- | --- | --- | --- |
| taxCode | TaxTreatment.TaxCode | TaxTreatment.TaxCode | TaxTreatment.TaxCode |
| productCode | TaxTreatment.ProductCode | TaxTreatment.ProductCode | TaxTreatment.ProductCode |
| productId | InvoiceLine.ProductId | InvoiceLine.ProductId | ProductId |
| amount | InvoiceLine.ChargeAmount | InvoiceLine.ChargeAmount | CreditMemoLine.ChargeAmount |
| effectiveDate | InvoiceLine.Invoice.InvoiceDate | If you're creating from negative lines, then this value is the original `Invoice.InvoiceDate` value. | CreditMemoLine.CreditMemo.CreditDate |
| lineNumber | InvoiceLine.ID | InvoiceLine.ID | CreditMemoLine.ID |
| description | InvoiceLine.Description | InvoiceLine.Description | CreditMemoLine.Description |
| quantity | InvoiceLine.Quantity | InvoiceLine.Quantity | NULL |
| **addresses** |  |  |  |
| billTo | InvoiceLine.BillingAddress.Address | InvoiceLine.BillingAddress.Address | CreditMemoLine.BillingAddress.Address |
| shipTo | InvoiceLine.ShippingAddress.Address | InvoiceLine.ShippingAddress.Address | CreditMemoLine.ShippingAddress.Address |
| shipFrom | InvoiceLine.ShippingFrom.Address | InvoiceLine.ShippingFrom.Address | CreditMemoLine.ShippingFrom.Address |
| soldTo | NULL | NULL | NULL |
| productsku | InvoiceLine.Product.productCode | InvoiceLine.Product.productCode | CreditMemoLine.Product.productCode |
| referenceDocumentCode | NULL | If you're converting from negative lines, then this value is the original `Document Code - "Invoice.ID" & "Debit" & TaxEngine.ID`. | If you're using standalone credit memo, then this value is NULL. Otherwise, this value is the `documentCode` value of the original invoice. |

## Response Mappings for Header Attributes

This table defines the response mappings between the header attributes of a tax callout and
fields of applicable objects. This response structure is used to create the InvoiceLineTax
records.

| Header Attributes | Invoice Mapping | Negative Invoice Mapping | Credit Mapping |
| --- | --- | --- | --- |
| currencyIsoCode | Invoice.CurrencyISOCode | Invoice.CurrencyISOCode | CreditMemo.CurrencyISOCode |
| isCommit | Not persisted. | Not persisted. | Not persisted. |
| referenceEntityId | Invoice.ID | Invoice.ID | CreditMemo.ID |
| taxEngineId | TaxTreatment.TaxEngine.ID | TaxTreatment.TaxEngine.ID | TaxTreatment.TaxEngine.ID |
| transactionDate | SystemDate | SystemDate | SystemDate |
| **sellerDetails** |  |  |  |
| code | TaxEngine.SellerCode | TaxEngine.SellerCode | TaxEngine.SellerCode |
| **customerDetails** |  |  |  |
| accountId | Invoice.BillingAccount.ID | Invoice.BillingAccount.ID | Invoice.BillingAccount.ID |
| code | Not persisted. | Not persisted. | Not persisted. |
| exemptionNo | Not persisted. | Not persisted. | Not persisted. |
| exemptionReason | Not persisted. | Not persisted. | Not persisted. |
| taxType | If status is `DRAFT`, then this value is `Estimated`. If status is `POSTED`, then this value is `Actual`. | If status is `DRAFT`, then this value is `Estimated`. If status is `POSTED`, then this value is `Actual`. | Actual |
| taxTransactionType | Debit | Credit | Credit |
| effectiveDate | invoice.InvoiceDate | If you're creating from negative lines, then this value is the original `Invoice.InvoiceDate` value. | If you're using standalone credit memo, then this value is the `CreditMemo.CreditDate` value. If you're creating from negative lines, then this value is the original `Invoice.InvoiceDate` value. |
| **addresses** |  |  |  |
| billTo | Not persisted. | Not persisted. | Not persisted. |
| shipTo | Not persisted. | Not persisted. | Not persisted. |
| shipFrom | Not persisted. | Not persisted. | Not persisted. |
| soldTo | Not persisted. | Not persisted. | Not persisted. |
| taxEngineAddress | Not persisted. | Not persisted. | Not persisted. |
| referenceDocumentCode | Not persisted. | Not persisted. | Not persisted. |
| description | Not persisted. | Not persisted. | Not persisted. |
| documentCode | Invoice.ID & "\_Debit\_" & TaxEngine.ID | Invoice.ID & "\_Credit\_" & TaxEngine.ID | CreditMemo.ID & "\_Credit\_" & TaxEngine.ID |
| status | Committed |  |  |
| **taxEngineLogs** |  |  |  |
| resultCode | TaxEngineInteractionLog.ResultCode | TaxEngineInteractionLog.ResultCode | TaxEngineInteractionLog.ResultCode |
| createddate | Not persisted. | Not persisted. | Not persisted. |
| Id | Not persisted. | Not persisted. | Not persisted. |
| transactionDate | Not persisted. | Not persisted. | Not persisted. |
| **amountDetails** |  |  |  |
| exemptAmount | Not persisted. | Not persisted. | Not persisted. |
| taxAmount | If header tax is enabled, then this value is `Invoice.TotalTaxesCapturedAtHeader`. | If header tax is enabled, then this value is `Invoice.TotalTaxesCapturedAtHeader`. | If header tax is enabled, then this value is `CreditMemo.TotalTaxesCapturedAtHeader`. |
| totalAmount | Not persisted. | Not persisted. | Not persisted. |
| totalAmountWithTax | Not persisted. | Not persisted. | Not persisted. |
| lineItems | Refer to the next line attributes section. | Refer to the next line attributes section. | Refer to the next line attributes section. |

## Response Mappings for Line Attributes

This table defines the response mappings between the line attributes of a tax callout and
fields of applicable objects.

| Line Attributes | Invoice Mapping | Negative Invoices | Credit Mapping |
| --- | --- | --- | --- |
| taxCode | InvoiceLineTax.taxCode | InvoiceLineTax.taxCode | InvoiceLineTax.taxCode |
| productCode | Not persisted. | Not persisted. | Not persisted. |
| productId | Not persisted. | Not persisted. | Not persisted. |
| **amountDetails** |  |  |  |
| exemptAmount | Not persisted. | Not persisted. | Not persisted. |
| taxAmount | Not persisted. | Not persisted. | Not persisted. |
| totalAmount | Not persisted. | Not persisted. | Not persisted. |
| totalAmountWithTax | Not persisted. | Not persisted. | Not persisted. |
| effectiveDate | InvoiceLineTax.taxEffectiveDate | InvoiceLineTax.taxEffectiveDate | CreditMemoLineTax.taxEffectiveDate |
| lineNumber | InvoiceLineTax.InvoiceLine | InvoiceLineTax.InvoiceLine | CreditMemoLineTax.CreditMemoLine |
| description | Not persisted. | Not persisted. | Not persisted. |
| quantity | Not persisted. | Not persisted. | Not persisted. |
| **addresses** |  |  |  |
| billTo | Not persisted. | Not persisted. | Not persisted. |
| shipTo | Not persisted. | Not persisted. | Not persisted. |
| shipFrom | Not persisted. | Not persisted. | Not persisted. |
| soldTo | Not persisted. | Not persisted. | Not persisted. |
| productsku | Not persisted. | Not persisted. | Not persisted. |
| referenceDocumentCode | Not persisted. | Not persisted. | Not persisted. |
| taxes | Refer to the next tax attributes section. | Refer to the next tax attributes section. | Refer to the next tax attributes section. |

## Response Mappings for Tax Attributes

This table defines the response mappings between the tax attributes of a tax callout and
fields of applicable objects.

| Line Attributes | Invoice Mapping | Negative Invoices | Credit Mapping |
| --- | --- | --- | --- |
| exemptAmount | InvoiceLineTax.taxExemptAmount | InvoiceLineTax.taxExemptAmount | Not persisted. |
| exemptReason | Not persisted. | Not persisted. | Not persisted. |
| **imposition** |  |  |  |
| type | Not persisted. | Not persisted. | Not persisted. |
| Name | InvoiceLineTax.TaxName | InvoiceLineTax.TaxName | CreditMemoLineTax.TaxName |
| **jurisdiction** |  |  |  |
| country | Not persisted. | Not persisted. | Not persisted. |
| id | Not persisted. | Not persisted. | Not persisted. |
| level | Not persisted. | Not persisted. | Not persisted. |
| name | Not persisted. | Not persisted. | Not persisted. |
| region | Not persisted. | Not persisted. | Not persisted. |
| stateAssignedNo | Not persisted. | Not persisted. | Not persisted. |
| rate | InvoiceLineTax.taxRate | InvoiceLineTax.taxRate | CreditMemoLineTax.TaxRate |
| tax | InvoiceLineTax.taxAmount | InvoiceLineTax.taxAmount | CreditMemoLineTax.TaxAmount |
| taxId | InvoiceLineTax.TaxTransactionNumber | InvoiceLineTax.TaxTransactionNumber | CreditMemoLineTax.TaxTransactionNumber |
| taxableAmount | Not persisted. | Not persisted. | Not persisted. |
