---
page_id: connect-resources-post-draft-credit-memo
title: Post a Draft Memo (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-post-draft-credit-memo.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_post_draft_credit_memo.htm
fetched_at: 2026-11-25
---

# Post a Draft Memo (POST)

Post a draft credit memo to a credit memo record for review and approval.

## Resource

```
/commerce/invoicing/credit/collection/actions/post
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v65.0/commerce/invoicing/credit/collection/actions/post
```

## Available Version

65.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
"creditMemoIds": ["50gDU00000001MnYAI"]
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `correlationId` | String | Splunk correlation ID to use to track messages that are related to the request and logged in Splunk by the different services involved in the request. If not specified, the service creates a random Universally Unique Identifier (UUID). | Optional | 65.0 |
| `creditMemoIds` | String[] | ID of the credit memo record in `Draft` status to be posted. You can post one draft credit memo per API request. | Required | 65.0 |

## Response Body for POST

[Credit Memo Post](./connect-responses-credit-memo-post-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-post-draft-credit-memo.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
