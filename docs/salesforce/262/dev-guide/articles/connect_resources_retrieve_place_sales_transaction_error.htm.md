---
page_id: connect_resources_retrieve_place_sales_transaction_error.htm
title: Retrieve Sales Transaction API Errors (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_retrieve_place_sales_transaction_error.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_business_apis_rest_references.htm
fetched_at: 2026-06-09
---

# Retrieve Sales Transaction API Errors (GET)

Retrieve any asynchronous error details associated with
a sales transaction request.

This API returns detailed error status and a retryable payload from [Place Sales Transaction API](./connect_resources_place_sales_transaction.htm.md "HTML (New Window)")
that runs asynchronously. Also, view any blocking errors that prevent a subrequest from
persisting. This request doesn’t return any non-blocking warnings, such as configuration or
tax warnings.

You can view the list of `rollbackedReferenceIds`, which
shows synthetic or reference IDs that roll back when the batch fails.

Resource
:   ```
    connect/revenue/transaction-management/sales-transactions/actions/place/trackerId/errors
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/revenue/transaction-management/sales-transactions/actions/place/16PRM0000004DBq/errors
    ```

Available version
:   66.0

HTTP methods
:   GET

Request parameter for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `includeRetryable​Payload` | Boolean | Indicates whether to return a subset of the original Place Sales Transaction API payload errors (`true`) or not (`false`). The default value is `false`. | Optional | 66.0 |

Response body for GET
:   [Sales Transaction
    Async Error](./connect_responses_place_sales_transaction_async_error_output.htm.md "Output representation of the details of errors encountered during the async processing of the Place Sales Transaction API request.")
