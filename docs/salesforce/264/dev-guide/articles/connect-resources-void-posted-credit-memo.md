---
page_id: connect-resources-void-posted-credit-memo
title: Void Posted Credit Memo (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-void-posted-credit-memo.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_void_posted_credit_memo.htm
fetched_at: 2026-11-25
---

# Void Posted Credit Memo (POST)

Void a credit memo in posted state.

The API response returns a unique identifier. In case of any asynchronous errors, a RevenueTransactionErrorLog record is created.

## Resource

```
/commerce/billing/credit-memos/{creditMemoId}/actions/void
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/commerce/billing/credit-memos/{50gVB0000003khRYAQ}/actions/void
```

## Available Version

66.0

## HTTP Methods

POST

## Path Parameter for POST

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `creditMemoId` | String | ID of the posted credit memo to be voided. | Required | 66.0 |

## Request Body for POST

As this API accepts a credit memo ID as a path parameter in the URL, specify an empty request body.

## Response Body for POST

[Void Posted Credit Memo](./connect-responses-void-posted-credit-memo-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-void-posted-credit-memo.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
