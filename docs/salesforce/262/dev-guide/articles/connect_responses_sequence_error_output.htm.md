---
page_id: connect_responses_sequence_error_output.htm
title: Sequence Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_sequence_error_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Sequence Error

Output representation of the error response that's associated with a request to create or
update a sequence policy, or assign sequences.

JSON example
:   This example shows a sample error
    response.

    ```
    {
      "error": {
        "errorCode": "INVALID_INPUT",
        "message": "Specify a valid selectionLogic."
      },
      "isSuccess": false,
      "sequencePolicyId": null
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Code for the resultant error. | Big, 65.0 | 65.0 |
| `message` | String | Error message for the resultant error. | Big, 65.0 | 65.0 |
