---
page_id: apex-connectapi-input-credit-memo-line-application
title: ConnectApi.CreditDetailsApplyInput
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-credit-memo-line-application.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-input-classes
legacy_page_id: apex_connectapi_input_credit_memo_line_application.htm
fetched_at: 2026-11-25
---

# ConnectApi.CreditDetailsApplyInput

Input representation of the request to specify one or more applications to apply a credit memo line for, with each application representing an invoice line.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `appliedAmount` | Double | Credit amount to be applied to the invoice line. | Required | 62.0 |
| `description` | String | Explanation or reason for applying the credit memo line. | Optional | 62.0 |
| `effectiveDate` | String | Effective date for the credit memo line. | Optional | 62.0 |
| `invoiceLineId` | String | ID of the invoice line record to apply the credit for. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-credit-memo-line-application.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
