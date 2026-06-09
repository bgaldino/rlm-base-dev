---
page_id: connect_responses_clone_sales_transaction_error_response.htm
title: Clone Sales Transaction Error Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_clone_sales_transaction_error_response.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Clone Sales Transaction Error Response

Output representation of the errors that occur during the clone sales transaction
operation.

JSON example
:   ```
    {
      "errors": [
        {
          "errorCode": "INVALID_API_INPUT",
          "message": "Specify only one record",
          "referenceId": "0QLxx0000004CBYGA2"
        }
      ]
    }
    ```

Properties
:   | Name | Type | Description | Available Version |
    | --- | --- | --- | --- |
    | `errorCode` | String | Code associated with the error. | 64.0 |
    | `message` | String | Message associated with the error. | 64.0 |
    | `referenceId` | String | Reference ID associated with the error. | 64.0 |
