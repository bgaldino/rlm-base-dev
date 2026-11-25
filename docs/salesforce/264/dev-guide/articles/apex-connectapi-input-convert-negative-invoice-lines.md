---
page_id: apex-connectapi-input-convert-negative-invoice-lines
title: ConnectApi.ConvertNegativeInvoiceLinesInputRequest
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-convert-negative-invoice-lines.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-input-classes
legacy_page_id: apex_connectapi_input_convert_negative_invoice_lines.htm
fetched_at: 2026-11-25
---

# ConnectApi.ConvertNegativeInvoiceLinesInputRequest

Input representation of the request details to convert a negative invoice line into a credit.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `description` | String | Description stamped on the credit memo that’s created after the negative invoice line conversion. | Optional | 62.0 |
| `effectiveDate` | String | Date stamped on the credit memo that’s created after the negative invoice line conversion. | Required | 62.0 |
| `invoiceId` | String | ID of the invoice whose negative invoice lines must be converted into a posted credit memo. | Required | 62.0 |
| `invoiceLines` | List<`String`> | Complete list of the negative invoice lines along with the associated invoice line taxes. The specified negative invoice lines are converted into a posted credit memo. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-convert-negative-invoice-lines.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
