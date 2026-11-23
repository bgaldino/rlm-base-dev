---
page_id: connect_requests_credit_memo_draft_to_posted_input.htm
title: Credit Memo Draft to Posted Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_credit_memo_draft_to_posted_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-11-23
---

# Credit Memo Draft to Posted Input

Input representation of the request to post a draft credit memo.

## JSON Example

```
{
"creditMemoIds": ["50gDU00000001MnYAI"]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `correlationId` | String | Splunk correlation ID to use to track messages that are related to the request and logged in Splunk by the different services involved in the request. If not specified, the service creates a random Universally Unique Identifier (UUID). | Optional | 65.0 |
| `creditMemoIds` | String[] | ID of the credit memo record in `Draft` status to be posted. You can post one draft credit memo per API request. | Required | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_credit_memo_draft_to_posted_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
