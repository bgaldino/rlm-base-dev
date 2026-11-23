---
page_id: apex_connectapi_output_void_posted_credit_memo_output.htm
title: ConnectApi.VoidPostedCreditMemoOutputRepresentation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_void_posted_credit_memo_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_output_classes.htm
fetched_at: 2026-11-23
---

# ConnectApi.VoidPostedCreditMemoOutputRepresentation

Output representation of the request to void a posted credit memo.

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `debitMemoId` | String | ID of the created debit memo. | 66.0 |
| `errors` | List<[`ConnectApi.ErrorResponse`](https://developer.salesforce.com/docs/atlas.en-us.264.0.apexref.meta/apexref/apex_connectapi_output_error_response.htm "HTML (New Window)")> | List of errors specific to this API request that were encountered during voiding the credit memo. | 66.0 |
| `isSuccess` | Boolean | Indicates whether the API request was successful (`true`) or not (`false`). | 66.0 |
| `statusURL` | String | Status URL for tracking this operation. | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_void_posted_credit_memo_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
