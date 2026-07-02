---
page_id: connect_responses_sequence_policy_output.htm
title: Sequence Policy
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_sequence_policy_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Sequence Policy

Output representation that shows the status of the assigned sequence pattern
values.

JSON example
:   This example shows a sample successful
    response.

    ```
    {
      "error": null,
      "isSuccess": true,
      "sequencePolicyId": "1Vdxx0000000GRNAA2"
    }
    ```
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
| `error` | [Sequence Error](./connect_responses_sequence_error_output.htm.md "Output representation of the error response that's associated with a request to create or update a sequence policy, or assign sequences.")[] | Details of any error that encountered during the processing of the API request. | Big, 65.0 | 65.0 |
| `isSuccess` | Boolean | Indicates whether the sequence policy is generated (`true`) or not (`false`). | Big, 65.0 | 65.0 |
| `sequencePolicyId` | String | ID of the sequence policy. | Big, 65.0 | 65.0 |
