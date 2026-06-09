---
page_id: connect_resources_clone_sales_transaction.htm
title: Clone Sales Transaction (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_clone_sales_transaction.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_business_apis_rest_references.htm
fetched_at: 2026-06-09
---

# Clone Sales Transaction (POST)

Create a clone of a sales transaction, such as a quote or an order.
You can also clone a quote line item or an order item record with its related records and
configurations.

This API supports the cloning of records for these objects.

- Quote
- QuoteLineItem
- OrderItem
- QuoteLineGroup
- Order
- OrderItemGroup

You can clone all items in a quote line group or order item group when the record to
clone is a quote line group or an order item group record.

Resource
:   ```
    /connect/rev/sales-transaction/actions/clone
    ```

Resource example
:   ```
    https://<varname>yourInstance</varname>.salesforce.com/services/data/v64.0/connect/rev/sales-transaction/actions/clone
    ```

Available version
:   64.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   This is a sample request to clone a record within a sales transaction.
    :   ```
        {
          "recordIds": ["0QLxx0000004CBYGA2"],
          "salesTransactionId": "0Q0xx0000004CE0CAM"
        }
        ```

        This is a sample request to clone all line items in a ramped group within a
        sales transaction.

        ```
        {
          "recordIds": ["0QLxx0000004CBYGA2"],
          "salesTransactionId": "0Q0xx0000004CE0CAM",
          "options": {
            "lineScope": "AllLines"
          }
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `recordIds` | String[] | ID of the record to be cloned. You can specify a single record ID only. | Required | 64.0 |
        | `salesTransactionId` | String | ID of the sales transaction related to the record IDs to clone. | Required | 64.0 |
        | `options` | [Clone Options Input](./connect_requests_clone_options_input.htm.md "Input representation of the options to clone a sales transaction.") | Specifies options to clone a ramp segment within a sales transaction. You can clone only the last ramp segment. | Optional | 65.0 |

Response body for POST
:   [Clone Sales
    Transaction](./connect_responses_clone_sales_transaction_output.htm.md "Output representation for the result of cloning records within a sales transaction.")
