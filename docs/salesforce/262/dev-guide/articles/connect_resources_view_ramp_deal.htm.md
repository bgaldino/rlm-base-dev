---
page_id: connect_resources_view_ramp_deal.htm
title: View Ramp Deal (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_view_ramp_deal.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_business_apis_rest_references.htm
fetched_at: 2026-06-09
---

# View Ramp Deal (GET)

View a ramp deal related to a quote line item or an order
item.

This API request retrieves the segments if the ramp deal already exists.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

This API is applicable when you're working with line
ramps. To work with ramp deals for groups, you must use the Place Sales Transaction API
and specify the `groupRampActions` property.

Resource
:   ```
    /connect/revenue-management/sales-transaction-contexts/resourceId/actions/ramp-deal-view
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/revenue-management/sales-transaction-contexts/0QLxx0000004CSOGA2/actions/ramp-deal-view?transactionId=0Q0xx0000004CDxCAM&transactionLineId=0QLxx0000004CSOGA2
    ```

Available version
:   62.0

HTTP methods
:   GET

Path parameter for GET
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `resourceId` | String | ID of the quote line item, order item, or context. | Required | 62.0 |

Request parameters for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `transaction​Id` | String | ID of the quote or order required to hydrate the context and retrieve the quote lines. | Required | 62.0 |
    | `transaction​LineId` | String | ID of the quote or order line required to retrieve the segmented details. | Required | 62.0 |

Response body for GET
:   [Ramp Deal
    Service](./connect_responses_ramp_deal_service_output.htm.md "Output representation of the details of a created, updated, or deleted ramp deal.")
