---
page_id: connect_responses_place_supplemental_transaction_output.htm
title: Supplemental Transaction
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_place_supplemental_transaction_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Supplemental Transaction

Output representation of the details of the created supplemental order.

JSON example
:   ```
    {
      "requestId": "16PRM0000004DBq",
      "statusURL": "/services/data/vXX.X/sobjects/AsyncOperationTracker/16PRM0000004DBq",
      "orderId": "801S70000001VKgIAM",
      "success": true,
      "errors": []
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Supplemental Transaction Error Response](./connect_responses_place_supplemental_transaction_error_response.htm.md "Output representation of the error details associated with the Place Supplemental Transaction API.")[] | List of errors encountered during synchronous processing. | Small, 64.0 | 64.0 |
| `requestId` | String | Request ID of the process that can be used to query the async status. | Small, 64.0 | 64.0 |
| `statusURL` | String | URL to check the status of the async operation, if available. | Small, 64.0 | 64.0 |
| `success` | Boolean | Indicates whether the synchronous part of the processing is successful (`true`) or not (`false`). | Small, 64.0 | 64.0 |
| `supplemental​TransactionId` | String | ID of the created supplemental transaction. | Small, 64.0 | 64.0 |
