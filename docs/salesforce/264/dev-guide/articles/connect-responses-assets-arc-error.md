---
page_id: connect-responses-assets-arc-error
title: ARC Base Error
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-assets-arc-error.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-responses
legacy_page_id: connect_responses_assets_arc_error.htm
fetched_at: 2026-11-25
---

# ARC Base Error

Output representation of the error response related to the amendment, renewal, or cancellation of assets.

```
    "errors": [ 
        { 
            "errorCode": "REQUIRED_FIELD_MISSING",
            "errorMessage": "Specify a value for quantityChange, and try again."
        } 
    ]
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error​Code` | String | Code for the resultant error. | Big, 62.0 | 62.0 |
| `error​Message` | String | Error message for the resultant error. | Big, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-assets-arc-error.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
