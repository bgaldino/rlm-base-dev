---
page_id: connect_responses_renew_output.htm
title: Renewal
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_renew_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Renewal

Output representation of the details of a renewal record.

JSON example
:   ```
    {
      "renewalRecordId": "0Q0xx0000004NsSCAU",
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
    | `errors` | [ARC Base Error](./connect_responses_assets_arc_error.htm.md "Output representation of the error response related to the amendment, renewal, or cancellation of assets.")[] | Error responses if the creation of a renewal record fails. | Small, 62.0 | 62.0 |
    | `renewal​RecordId` | String | ID of the renewal record that’s created for the Quote or Order record. | Small, 62.0 | 62.0 |
    | `requestId` | String | Request ID that’s used to track the async request. | Small, 62.0 | 62.0 |
    | `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
