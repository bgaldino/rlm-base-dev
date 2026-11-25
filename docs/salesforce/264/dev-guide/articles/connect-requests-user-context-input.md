---
page_id: connect-requests-user-context-input
title: User Context Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-user-context-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-api-requests
legacy_page_id: connect_requests_user_context_input.htm
fetched_at: 2026-11-25
---

# User Context Input

Input representation of the details with the user context.

## JSON Example

```
    "userContext": {
        "accountId": "001xx0000000001AAA",
        "contactId": "003xx00000000D7AAI",
        "contextId": "e055bb18-d4e8-41c3-881e-0132b9561708"
    }
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `account​Id` | String | ID of the account in a user context. | Optional | 60.0 |
| `contact​Id` | String | ID of the contact in a user context. | Optional | 60.0 |
| `context​Id` | String | ID of the context that represents the created session. | Optional | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-user-context-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
