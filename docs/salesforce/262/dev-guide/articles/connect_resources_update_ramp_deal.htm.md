---
page_id: connect_resources_update_ramp_deal.htm
title: Update Ramp Deal (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_update_ramp_deal.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_business_apis_rest_references.htm
fetched_at: 2026-06-09
---

# Update Ramp Deal (POST)

Modify a ramp deal in scenarios where a segment has updates such as
quantity, discount, or date change.

Update a ramp deal in these scenarios.

- A segment has quantity or discount changes.
- A trial segment or custom segment has a date change. A custom segment is an added or
  deleted segment. In this scenario, you can update a ramp deal during the initial sale
  before assetization.

This API request returns the updated context with the context ID. You must call the Place Sales
Transaction (POST) API by specifying this context ID to apply the ramp deal updates. See
[Place Sales Transaction (POST)
API](https://developer.salesforce.com/docs/./connect_resources_place_sales_transaction.htm.md "HTML (New Window)").

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

This API is applicable when you're working with line
ramps. To work with ramp deals for groups, you must use the Place Sales Transaction API
and specify the `groupRampActions` property.

Resource
:   ```
    /connect/revenue-management/sales-transaction-contexts/resourceId/actions/ramp-deal-update
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/revenue-management/sales-transaction-contexts/4f23961a5c98806f89305e064c67b397e93f1bb8a2a7a3a80db506f1d4110ee9/actions/ramp-deal-update
    ```

Available version
:   62.0

HTTP methods
:   POST

Path parameter for POST
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `resourceId` | String | ID of the context data that’s used to build the pricing procedure. Get the context instance ID by invoking the Context Service API. See [Context Service (POST)](https://developer.salesforce.com/docs/atlas.en-us.262.0.industries_reference.meta/industries_reference/connect_resources_create_context.htm "HTML (New Window)"). | Required | 62.0 |

Request body for POST
:   JSON example
    :   ```
        {
          "executionSettings": {
               "executePricing": true,
               "executeConfigRules": false
          },
          "addedNodes": [
            {
              "contextNodePath": [
                "4f23961a5c98806f89305e064c67b397e93f1bb8a2a7a3a80db506f1d4110ee9", // Context ID
                "0Q0xx0000004CPACA2", //Quote or Order ID
                "RandomUUID" // random UUID for Quote Line Item or Order Item ID
              ],
              "contextNode": {
                 "Discount": 10,
                 "Quantity": 5,
                 "ItemSegmentName": "Year 5",
                 "StartDate":"2024-09-07T00:00:00.000Z",
                 "EndDate":"2024-09-07T00:00:00.000Z"
              }
            }
          ],
          "updatedNodes": [
             {
              "contextNodePath": [
                "4f23961a5c98806f89305e064c67b397e93f1bb8a2a7a3a80db506f1d4110ee9", // Context ID
                "0Q0xx0000004CPACA2", //Quote or Order ID
                "0QLxx0000004CfIGAU" // Quote Line ID or Order Line ID to update
              ],
              "contextNode": {
                  "Discount": 10,
                  "Quantity": 5
              }
            } 
          ],
          "deletedNodes": [
            {
              "contextNodePath": [
                "4f23961a5c98806f89305e064c67b397e93f1bb8a2a7a3a80db506f1d4110ee9",
                "0Q0xx0000004CPACA2",
                "0QLxx0000004CfIGAU" // Quote Line Item ID to delete
              ]
            }
          ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `added​Nodes` | [Context Node Input](./connect_requests_context_node_input.htm.md "Input representation of the details of the context nodes for ramp segments.")[] | Details of the nodes to be added. | Required | 62.0 |
        | `deleted​Nodes` | [Context Node Input](./connect_requests_context_node_input.htm.md "Input representation of the details of the context nodes for ramp segments.")[] | Details of the nodes to be deleted. | Required | 62.0 |
        | `execution​Settings` | [Execution Settings Input](./connect_requests_execution_settings_input.htm.md "Input representation of the execution settings for a ramp deal.")[] | Settings to run the pricing or configuration rules. | Optional | 62.0 |
        | `updated​Nodes` | [Context Node Input](./connect_requests_context_node_input.htm.md "Input representation of the details of the context nodes for ramp segments.")[] | Details of the nodes to be updated. | Required | 62.0 |

Response body for POST
:   [Ramp Deal
    Service](./connect_responses_ramp_deal_service_output.htm.md "Output representation of the details of a created, updated, or deleted ramp deal.")
