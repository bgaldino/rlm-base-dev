---
page_id: apex-connectapi-input-credit-memo-apply
title: ConnectApi.CreditMemoApplyInputRequest
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-credit-memo-apply.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-input-classes
legacy_page_id: apex_connectapi_input_credit_memo_apply.htm
fetched_at: 2026-11-25
---

# ConnectApi.CreditMemoApplyInputRequest

Input representation of the request to apply a credit memo to an invoice.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `applications` | List<[ConnectApi.ApplicationsRequest](./apex-connectapi-input-credit-memo-apply-application.md)> | List of one or more applications to apply the credit memo for. Each application represents an invoice that’s credited by using the balance of the specified credit memo. | Required | 62.0 |
| `creditMemoId` | String | ID of the credit memo record. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-credit-memo-apply.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
