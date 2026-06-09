---
page_id: apex_connectapi_input_credit_invoice_invoice_line.htm
title: ConnectApi.CreditInvoiceInvoiceLine
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_credit_invoice_invoice_line.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.CreditInvoiceInvoiceLine

Input representation of the details of the invoice lines to be credited.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `addresses` | [ConnectApi.CreditMemoAddressesInputRequest](./apex_connectapi_input_credit_memo_addresses.htm.md "Input representation of the details of the billing and shipping addresses.") | Addresses to be created manually for this invoice line and the overridden tax lines. These addresses are only applicable if this invoice line is using the `ManualOverride` tax strategy. | Optional | 62.0 |
| `amountToCredit` | Double | Amount to be credited from this invoice line. | Required | 62.0 |
| `invoiceLineId` | String | ID of the invoice line record to be credited. The invoice line ID must be related to the invoice ID specified in the API request. | Required | 62.0 |
| `isTaxOnlyCredit` | Boolean | Indicates whether the applicable tax amount is credited for the charge or adjustment amount (`true`), or the applicable tax amount is credited along with the charge or adjustment amount (`false`). The default value is `false`. | Optional | 62.0 |
| `taxEffectiveDate` | String | Date when the tax takes effect and the invoice line is credited. | Optional | 62.0 |
| `taxStrategy` | `ConnectApi.TaxStrategyEnum` | Tax strategy for crediting the invoice line. This tax strategy takes precedence over the `taxStrategy` property value specified in the [Credit Invoice Input](./connect_requests_credit_invoice_input.htm.md "Input representation of the details of the request to create a credit memo."). Valid values are:   - `Ignore`—Specifies that the   creation of tax lines must be ignored. - `ManualOverride`—Specifies that the provided tax values must be   considered for taxes. - `CopyFromInvoiceLine`—Specifies   that tax values must be copied from the invoice line. - `Calculate`—Specifies that tax   must be calculated by using the API. | Optional | 62.0 |
| `taxes` | List<[ConnectApi.CreditInvoiceInvoiceLineTax](./apex_connectapi_input_credit_invoice_invoice_line_tax.htm.md "Input representation of the details of the tax lines to be created manually for the invoice line.")> | List of tax lines to be created manually for this invoice line. | Required if the `taxStrategy` property value is `ManualOverride`. | 62.0 |
