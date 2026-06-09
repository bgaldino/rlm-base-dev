---
page_id: apex_connectapi_input_credit_invoice.htm
title: ConnectApi.CreditInvoiceInputRequest
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_credit_invoice.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.CreditInvoiceInputRequest

Input representation of the details of the request to create a credit memo.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `description` | String | Description for the credit memo to be created. | Optional | 62.0 |
| `effective​Date` | String | Date when the credit memo takes effect. | Optional | 62.0 |
| `invoice​Lines` | List<[ConnectApi.CreditInvoiceInvoiceLine](./apex_connectapi_input_credit_invoice_invoice_line.htm.md "Input representation of the details of the invoice lines to be credited.")> | List of the invoice lines to be credited. The invoice line IDs must be related to the invoice ID specified in the API request. If invoice lines aren’t specified, the API request results in an error. | Required | 62.0 |
| `taxEffective​Date` | String | Date when the tax takes effect to recalculate the taxes. | Optional | 62.0 |
| `tax​Strategy` | `ConnectApi.TaxStrategyEnum` | Tax strategy to be applied across invoice lines. You can override the tax strategy at the individual invoice line level or at the tax line level. Valid values are:   - `Ignore`—Specifies that the   creation of tax lines must be ignored. - `ManualOverride`—Specifies that the provided tax values must be   considered for taxes. - `CopyFromInvoiceLine`—Specifies   that tax values must be copied from the invoice line. - `Calculate`—Specifies that tax   must be calculated by using the API. | Required | 62.0 |
| `type` | `ConnectApi.CreditMemoTypeEnum` | Type of credit memo to be created. Valid values are `Posted` and `Draft`. Specify `Draft` as a value in your request to create draft credit memos. | Optional | 62.0 |
