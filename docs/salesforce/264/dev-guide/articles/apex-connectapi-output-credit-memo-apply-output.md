---
page_id: apex-connectapi-output-credit-memo-apply-output
title: ConnectApi.ApplyCreditResult
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-output-credit-memo-apply-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-output-classes
legacy_page_id: apex_connectapi_output_credit_memo_apply_output.htm
fetched_at: 2026-11-25
---

# ConnectApi.ApplyCreditResult

Connect API representation of credit memo apply output result

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `appliedToId` | String | ID of the invoice record that the credit is applied to. | 62.0 |
| `errors` | List<[ConnectApi.ErrorResponse](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_connectapi_output_error_response.htm)> | List of errors encountered during the processing of the API request. | 62.0 |
| `id` | String | ID of the credit memo invoice application. | 62.0 |
| `success` | Boolean | Indicates whether the credit memo is successfully applied (`true`) or not (`false`). | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-output-credit-memo-apply-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
