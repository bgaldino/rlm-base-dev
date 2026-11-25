---
page_id: connect-responses-context-aware-billing-schedule-output
title: Context-Aware Billing Schedule
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-context-aware-billing-schedule-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_context_aware_billing_schedule_output.htm
fetched_at: 2026-11-25
---

# Context-Aware Billing Schedule

Output representation of the context-aware billing schedule.

## JSON Example

This request shows a sample success response.

```
{ 
    "errors": null, 
    "requestIdentifier": "16Pxx0000004CaS", 
    "statusURL": "/services/data/v68.0/sobjects/AsyncOperationTracker/16Pxx0000004CaSEAU", 
    "success": true 
}
```

This request shows a sample error response.

```
{ 
    "errors": [ 
        { 
            "errorCode": "REQUIRED_FIELD_MISSING",
            "errorMessage": "Required fields are missing: billToContact", 
            "referenceId": "802xx000001nmb5"
        } 
    ],
    "requestIdentifier": "16Pxx0000004CYq", 
    "statusURL": "/services/data/v68.0/sobjects/AsyncOperationTracker/16Pxx0000004CYqEAM", 
    "success": false 
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Context Aware Billing Schedule Error](./connect-responses-context-aware-billing-schedule-error.md)[] | Error response if the generation of the billing schedule fails. | Big, 62.0 | 62.0 |
| `request​Identifier` | String | Unique request identifier that you can use to poll the asynchronous request. | Big, 62.0 | 62.0 |
| `statusURL` | String | Status URL to track the operation. | Big, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the processing of the billing schedule is successful (`true`) or not (`false`). | Big, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-context-aware-billing-schedule-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
