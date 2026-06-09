---
page_id: connect_responses_clone_sales_transaction_output.htm
title: Clone Sales Transaction
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_clone_sales_transaction_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Clone Sales Transaction

Output representation for the result of cloning records within a sales transaction.

JSON example
:   This example shows a sample of a successful
    response.

    ```
    {
        "requestId": "9356bcbf04f06e22360a09807c13e1d4e395",
        "salesTransactionId": "0Q0SG000000ACxf0AG",
        "errors": [],
        "success": true
    }
    ```

    This example shows a sample error
    response.

    ```
    {
        "requestId": "9356bcbf04f06e22360a09807c13e1d4e395",
        "salesTransactionId": "0Q0SG000000ACxf0AG",
        "errors": [
            {
                "errorCode": "INVALID_API_INPUT",
                "message": "Specify only one record",
                "referenceId": "0QLxx0000004CBYGA2"
            }
        ],
        "success": false
    }
    ```

Properties
:   | Name | Type | Description | Available Version |
    | --- | --- | --- | --- |
    | `requestId` | String | Request ID of the process that can be used to query the async status. | 64.0 |
    | `salesTransactionId` | String | ID of the quote line item, order item, quote line group, or order item group record. | 64.0 |
    | `success` | Boolean | Indicates whether the synchronous part of the processing is successful (`true`) or not (`false`). | 64.0 |
    | `errors` | [Clone Sales Transaction Error Response](./connect_responses_clone_sales_transaction_error_response.htm.md "Output representation of the errors that occur during the clone sales transaction operation.")[] | List of errors encountered during synchronous processing. | 64.0 |
