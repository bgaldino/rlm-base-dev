---
page_id: connect_requests_clone_sales_transaction_input.htm
title: Clone Sales Transaction Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_clone_sales_transaction_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-06-09
---

# Clone Sales Transaction Input

Input representation of the request to clone records within a sales
transaction.

JSON example
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
