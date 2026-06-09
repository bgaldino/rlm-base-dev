---
page_id: connect_responses_cancel_output.htm
title: Cancellation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_cancel_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Cancellation

Output representation of the details of a cancellation record.

JSON example
:   ```
    {
      "cancellationRecordId": "0Q0xx0000004NsSCAU",
      "errors": [
        {
          "errorCode": "REQUIRED_FIELD_MISSING",
          "errorMessage": "Specify a value for quantityChange, and try again."
        }
      ],
      "requestId": "16Pxx0000004NIy",
      "success": true
    }
    ```

Properties
:   | Property Name | Type | Description | Filter Group and Version | Available Version |
    | --- | --- | --- | --- | --- |
    | `cancellation​RecordId` | String | ID of the cancellation record that’s created for a quote or an order. | Small, 62.0 | 62.0 |
    | `errors` | [ARC Base Error](./connect_responses_assets_arc_error.htm.md "Output representation of the error response related to the amendment, renewal, or cancellation of assets.")[] | Error responses if the creation of a cancellation record fails. | Small, 62.0 | 62.0 |
    | `requestId` | String | Request ID that’s used to track the async request. | Small, 62.0 | 62.0 |
    | `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
