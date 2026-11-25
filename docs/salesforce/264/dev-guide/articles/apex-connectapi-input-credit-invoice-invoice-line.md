---
page_id: apex-connectapi-input-credit-invoice-invoice-line
title: ConnectApi.CreditInvoiceInvoiceLine
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-credit-invoice-invoice-line.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-input-classes
legacy_page_id: apex_connectapi_input_credit_invoice_invoice_line.htm
fetched_at: 2026-11-25
---

# ConnectApi.CreditInvoiceInvoiceLine

Input representation of the details of the invoice lines to be credited.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `addresses` | [ConnectApi.CreditMemoAddressesInputRequest](./apex-connectapi-input-credit-memo-addresses.md) | Addresses to be created manually for this invoice line and the overridden tax lines. These addresses are only applicable if this invoice line is using the `ManualOverride` tax strategy. | Optional | 62.0 |
| `amountToCredit` | Double | Amount to be credited from this invoice line. | Required | 62.0 |
| `invoiceLineId` | String | ID of the invoice line record to be credited. The invoice line ID must be related to the invoice ID specified in the API request. | Required | 62.0 |
| `isTaxOnlyCredit` | Boolean | Indicates whether the applicable tax amount is credited for the charge or adjustment amount (`true`), or the applicable tax amount is credited along with the charge or adjustment amount (`false`). The default value is `false`. | Optional | 62.0 |
| `taxEffectiveDate` | String | Date when the tax takes effect and the invoice line is credited. | Optional | 62.0 |
| `taxStrategy` | `ConnectApi.TaxStrategyEnum` | Tax strategy for crediting the invoice line. This tax strategy takes precedence over the `taxStrategy` property value specified in the [Credit Invoice Input](./connect-requests-credit-invoice-input.md). | Optional | 62.0 |
| `taxes` | List<[ConnectApi.CreditInvoiceInvoiceLineTax](./apex-connectapi-input-credit-invoice-invoice-line-tax.md)> | List of tax lines to be created manually for this invoice line. | Required if the `taxStrategy` property value is `ManualOverride`. | 62.0 |

taxStrategy values:

- `Ignore`—Specifies that the creation of tax lines must be ignored.

- `ManualOverride`—Specifies that the provided tax values must be considered for taxes.

- `CopyFromInvoiceLine`—Specifies that tax values must be copied from the invoice line.

- `Calculate`—Specifies that tax must be calculated by using the API.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-credit-invoice-invoice-line.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
