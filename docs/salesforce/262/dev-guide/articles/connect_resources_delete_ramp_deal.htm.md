---
page_id: connect_resources_delete_ramp_deal.htm
title: Delete Ramp Deal (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_delete_ramp_deal.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_business_apis_rest_references.htm
fetched_at: 2026-06-09
---

# Delete Ramp Deal (POST)

Delete a ramp deal to convert a ramped product to include a single
quote line item or order item.

This API request deletes the segments related to the product. The API response includes the
updated context with the context ID. You must call the Place Sales Transaction (POST) API by
specifying this context ID to apply the ramp deal updates. See [Place Sales Transaction (POST)
API](./connect_resources_place_sales_transaction.htm.md "HTML (New Window)").

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

This API is applicable when you're working with line
ramps. To work with ramp deals for groups, you must use the Place Sales Transaction API
and specify the `groupRampActions` property.

Resource
:   ```
    /connect/revenue-management/sales-transaction-contexts/resourceId/actions/ramp-deal-delete
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/revenue-management/sales-transaction-contexts/0QLxx0000004CfIGAU/actions/ramp-deal-delete
    ```

Available version
:   62.0

HTTP methods
:   POST

Path parameter for POST
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `resourceId` | String | ID of the context. | Required | 62.0 |

Request body for POST
:   JSON example
    :   ```
        {
          "rampDealIds": [
            "0Q0xx0000004CDxCAM",
            "0QLxx0000004CSOGA2"
          ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `rampDeal​Ids` | String[] | Ramp identifier on the quote line item or order item. | Required | 62.0 |

Response body for POST
:   [Ramp Deal
    Service](./connect_responses_ramp_deal_service_output.htm.md "Output representation of the details of a created, updated, or deleted ramp deal.")
