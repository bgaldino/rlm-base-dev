---
page_id: connect_responses_context_aware_billing_schedule_error.htm
title: Context-Aware Billing Schedule Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_context_aware_billing_schedule_error.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Context-Aware Billing Schedule Error

Output representation of the error response related to the generation of the billing
schedule.

```
    "errors": [ 
        { 
            "errorCode": "REQUIRED_FIELD_MISSING",
            "errorMessage": "Required fields are missing: billToContact", 
            "referenceId": "802xx000001nmb5"
        } 
    ]
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Code for the resultant error. | Big, 62.0 | 62.0 |
| `errorMessage` | String | Error message for the resultant error. | Big, 62.0 | 62.0 |
| `referenceId` | String | Reference ID of the source item that resulted in the error. | Big, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_context_aware_billing_schedule_error.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
