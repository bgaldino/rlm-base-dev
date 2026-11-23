---
page_id: apex_connectapi_output_credit_memo_line_applied_response.htm
title: ConnectApi.AppliedCreditResponse
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_credit_memo_line_applied_response.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_output_classes.htm
fetched_at: 2026-11-23
---

# ConnectApi.AppliedCreditResponse

Output representation of the list of applied credit memo line results.

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `creditMemoLineInvoiceLineId` | String | ID of the credit memo line invoice line ID. | 62.0 |
| `errors` | List<[`ConnectApi.ErrorResponse`](https://developer.salesforce.com/docs/atlas.en-us.264.0.apexref.meta/apexref/apex_connectapi_output_error_response.htm "HTML (New Window)")> | List of errors encountered during the processing of the API request. | 62.0 |
| `invoiceLineId` | String | ID of the invoice line record that the credit is applied to. | 62.0 |
| `success` | Boolean | Indicates whether the credit memo line is successfully applied (`true`) or not (`false`). | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_credit_memo_line_applied_response.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
