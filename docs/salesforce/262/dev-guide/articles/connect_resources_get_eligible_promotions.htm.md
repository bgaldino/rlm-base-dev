---
page_id: connect_resources_get_eligible_promotions.htm
title: Get Eligible Promotions (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_eligible_promotions.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_business_apis_rest_references.htm
fetched_at: 2026-06-09
---

# Get Eligible Promotions (POST)

Get eligible promotions for line items within a quote or an
order.

This API accepts line item IDs and sales transaction ID as the input and then
initializes the context by filtering on the specific line items.

Resource
:   ```
    /revenue/transaction-management/sales-transactions/actions/get-eligible-promotions
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/revenue/transaction-management/sales-transactions/actions/get-eligible-promotions
    ```

Available version
:   66.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "salesTransactionId": "0Q0xx0000004EOECA2",
          "lineItemIds": [
            "0QLxx0000004E7eGAE",
            "0QLxx0000004GCeGAM",
            "0QLxx0000004E7gGAE"
          ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `lineItemIds` | String[] | List of line item IDs to evaluate for promotions. The object type is auto-determined from the sales transaction ID. | Required | 66.0 |
        | `salesTransactionId` | String | The sales transaction ID, such as an order ID or a quote ID, for the promotion evaluation. | Required | 66.0 |

Response body for POST
:   [Get Eligible
    Promotions](./connect_responses_get_eligible_promotions_output.htm.md "Output representation of the details of the eligible promotions.")
