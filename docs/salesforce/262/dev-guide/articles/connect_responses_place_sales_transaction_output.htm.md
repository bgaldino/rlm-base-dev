---
page_id: connect_responses_place_sales_transaction_output.htm
title: Sales Transaction
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_place_sales_transaction_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Sales Transaction

Output representation of the request to create a sales transaction.

JSON example
:   ```
    {
      "contextDetails": {
        "contextId": "e055bb18-d4e8-41c3-881e-0132b9561708",
        "isBuiltInTransaction": true
      },
      "errorResponse": {
        "errorCode": "INVALID_API_INPUT",
        "message": "Include record type and method in the request and try again.",
        "referenceId": "refQuoteItem2"
      },
      "isSuccess": true,
      "salesTransactionId": "0Q0xx0000004CNYCA2",
      "statusUrl": null,
      "trackerId": null
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextDetails` | [Sales Transaction Context](./connect_responses_sales_transaction_context_output.htm.md "Output representation of the context details that are associated with a sales transaction.") | Details of the context that’s created for the sales transaction. | Small, 63.0 | 63.0 |
| `errorResponse` | [Sales Transaction Error Response](./connect_responses_place_sales_transaction_error_response.htm.md "Output representation of the error details associated with the API request.")[] | Details of the error if the operation fails. | Small, 63.0 | 63.0 |
| `isSuccess` | Boolean | Indicates if the operation is successful (`true`) or not (`false`). | Small, 63.0 | 63.0 |
| `salesTransactionId` | String | ID of the sales transaction, such as a quote or an order. | Small, 63.0 | 63.0 |
| `statusUrl` | String | URL to check the status of the operation. | Small, 63.0 | 63.0 |
| `trackerId` | String | Unique identifier assigned to a specific operation or request that's used for tracking and referencing the operation. | Small, 63.0 | 63.0 |

The **Calculation Status** field for a quote or an order shows
an intermediate status as `Saving` during the creation of
a sales transaction. If the pricing calculation fails, then the **Calculation
Status** field shows the `Pricing Calculation
Failed` status. See [Quote standard object](https://developer.salesforce.com/docs/atlas.en-us.254.0.object_reference.meta/object_reference/sforce_api_objects_quote.htm "HTML (New Window)") for a
list of applicable calculation status values.
