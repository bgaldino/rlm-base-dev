---
page_id: connect_responses_context_aware_billing_schedule_output.htm
title: Context-Aware Billing Schedule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_context_aware_billing_schedule_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Context-Aware Billing Schedule

Output representation of the context-aware billing schedule.

JSON example
:   This request shows a sample success response.
:   ```
    { 
        "errors": null, 
        "requestIdentifier": "16Pxx0000004CaS", 
        "statusURL": "/services/data/v67.0/sobjects/AsyncOperationTracker/16Pxx0000004CaSEAU", 
        "success": true 
    }
    ```
:   This request shows a sample error response.
:   ```
    { 
        "errors": [ 
            { 
                "errorCode": "REQUIRED_FIELD_MISSING",
                "errorMessage": "Required fields are missing: billToContact", 
                "referenceId": "802xx000001nmb5"
            } 
        ],
        "requestIdentifier": "16Pxx0000004CYq", 
        "statusURL": "/services/data/v67.0/sobjects/AsyncOperationTracker/16Pxx0000004CYqEAM", 
        "success": false 
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Context Aware Billing Schedule Error](./connect_responses_context_aware_billing_schedule_error.htm.md "Output representation of the error response related to the generation of the billing schedule.")[] | Error response if the generation of the billing schedule fails. | Big, 62.0 | 62.0 |
| `request​Identifier` | String | Unique request identifier that you can use to poll the asynchronous request. | Big, 62.0 | 62.0 |
| `statusURL` | String | Status URL to track the operation. | Big, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the processing of the billing schedule is successful (`true`) or not (`false`). | Big, 62.0 | 62.0 |
