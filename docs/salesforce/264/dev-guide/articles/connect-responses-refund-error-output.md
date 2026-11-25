---
page_id: connect-responses-refund-error-output
title: Refund Error
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-refund-error-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: connect-responses-refund-credit-memo-output
legacy_page_id: connect_responses_refund_error_output.htm
fetched_at: 2026-11-25
---

# Refund Error

Output representation of an error that occurred during a refund against a credit memo.

## JSON Example

```
{
  "errorCode": "AMOUNT_EXCEEDS_BALANCE",
  "message": "The refund amount exceeds the remaining balance on the credit memo."
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error​Code` | String | Code that represents the error, for example `INVALID_CREDIT_MEMO`, `AMOUNT_EXCEEDS_BALANCE`, or `CREDIT_MEMO_LOCKED`. | Big, 68.0 | 68.0 |
| `message` | String | Message that states the reason for the error. | Big, 68.0 | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-refund-error-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
