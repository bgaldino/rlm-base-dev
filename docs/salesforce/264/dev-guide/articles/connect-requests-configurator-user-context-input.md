---
page_id: connect-requests-configurator-user-context-input
title: User Context Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-configurator-user-context-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: product-configurator-business-apis-requests
legacy_page_id: connect_requests_configurator_user_context_input.htm
fetched_at: 2026-11-25
---

# User Context Input

Input representation of the request to get the context details of a user, which are used for qualification rules.

## JSON Example

```
    "qualificationContext": {
        "accountId": "001DU000001nHUGYA2",
        "contactId": "003xx00000000D7AAI"
    }
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `accountId` | String | ID of the account in a user context. | Optional | 60.0 |
| `contactId` | String | ID of the contact in a user context. | Optional | 60.0 |
| `contextId` | String | ID of the context that represents the created session. | Optional | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-configurator-user-context-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
