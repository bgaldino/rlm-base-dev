---
page_id: connect_responses_sequences_assignment_result_output.htm
title: Sequences Assignment Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_sequences_assignment_result_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Sequences Assignment Result

Output representation of the details of the assigned sequence values to target
objects.

JSON example
:   This example shows a sample successful
    response.

    ```
    {
      "errors": null,
      "sequencesAssignment": [
        {
          "errors": null,
          "isSuccess": true,
          "sequencePatternValue": "INV-1234-2025-04-12-001",
          "targetObjectId": "3ttxx000000085dAAA"
        }
      ],
      "status": "Success"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Sequence Error](./connect_responses_sequence_error_output.htm.md "Output representation of the error response that's associated with a request to create or update a sequence policy, or assign sequences.")[] | Error encountered during the processing of the API request. | Big, 65.0 | 65.0 |
| `isSuccess` | Boolean | Indicates whether the sequence pattern value is assigned (`true`) or not (`false`). | Big, 65.0 | 65.0 |
| `sequencePatternValue` | String | Sequence pattern value assigned to the target object. | Big, 65.0 | 65.0 |
| `sequencePolicyId` | String | ID of the sequence policy assigned to the target object. | Big, 65.0 | 65.0 |
| `targetObjectId` | String | Record to which the sequence pattern value is assigned. | Big, 65.0 | 65.0 |
