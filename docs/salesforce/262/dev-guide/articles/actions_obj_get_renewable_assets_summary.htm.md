---
page_id: actions_obj_get_renewable_assets_summary.htm
title: Get Renewable Assets Summary Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_get_renewable_assets_summary.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Get Renewable Assets Summary Action

Retrieve details about renewable assets in a given order. You can
use this information to create renewal opportunities.

This action gets pricing data from the OrderEntitiesMapping context mapping
within the SalesTransactionContext context definition. Before you use this action,
edit the context mapping to map the objects and fields used in your pricing
procedure to the nodes and attributes in the context definition.

This action
doesn’t support providing a summary with procedure plans. As a result, renewal line
items may return a price of zero.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

#### Note

We recommend adding the same fields and
mappings for the Quote and Order objects, and for the Quote Line Item and Order
Product objects.

This action is available in API version 64.0 and
later.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/getRenewableAssetsSummary`

Formats
:   JSON, XML

HTTP Methods
:   POST

Authentication
:   `Authorization:
    Bearertoken`

## Inputs

| Input | Details |
| --- | --- |
| orderId | Type  id  Description  Required.  ID of the order related to the assets to check for renewal opportunities. |

## Outputs

| Output | Details |
| --- | --- |
| renewableAssetsSummary | Type  Apex-defined  Description  Summary of the assets associated with the order, including details about renewal opportunities such as renewal pricing information. See [renew\_assets\_summary Apex Namespace](./apex_namespace_renew_assets_summary.htm.md "HTML (New Window)"). |

## Example

POST
:   Here's a sample request for the Get Renewable Assets Summary action.

    ```
    {
      "inputs": [
        {
          "orderId": "801xx000003GZ39AAG"
        }
      ]
    }
    ```
:   Here's a sample response for the Get Renewable Assets Summary action.

    ```
    [
      {
        "actionName": "getRenewableAssetsSummary",
        "errors": null,
        "invocationId": null,
        "isSuccess": true,
        "outcome": null,
        "outputValues": {
          "renewableAssetsSummary": [
            {
              "startDate": "2025-07-22",
              "rootAssetOpportunity": null,
              "renewalPriceDetails": [
                {
                  "quantity": 1,
                  "netUnitPrice": 0
                }
              ],
              "productId": "01txx0000006i3DAAQ",
              "priceBookId": "01sxx0000005ptpAAA",
              "priceBookEntryId": "01uxx0000008yXCAAY",
              "orderItem": "802xx000001nb1LAAQ",
              "opportunityProductId": null,
              "lastAssetActionSubtype": null,
              "lastAssetAction": "Initial Sale",
              "endDate": "2025-08-21",
              "assetId": "02ixx0000004HKwAAM",
              "account": "001xx000003GZ1XAAW"
            }
          ]
        },
        "sortOrder": -1,
        "version": 1
      }
    ]
    ```
