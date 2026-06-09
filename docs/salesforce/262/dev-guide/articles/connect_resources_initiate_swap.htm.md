---
page_id: connect_resources_initiate_swap.htm
title: Initiate Swap (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_initiate_swap.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_business_apis_rest_references.htm
fetched_at: 2026-06-09
---

# Initiate Swap (POST)

Exchange one product for another of equivalent or different value. The
change is tracked as a swap request with linked asset actions and a net-zero order total where
applicable. The API creates an amendment quote and order with order actions and quote action
subtypes.

When the order is assetized, the source asset gets an asset action with business category
as `Swap` (reduced quantity). The new asset is created
with an asset action that identifies it as swapped in, with relationships that link the
swapped-from and swapped-to assets. The swaps are auditable and reportable separately from
cancellations and new sales. This API also supports use cases such as trading unused
licenses for credits or moving spend between products while preserving contract intent.

Resource
:   ```
    /revenue/transaction-management/assets/actions/swap
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/revenue/transaction-management/assets/actions/swap
    ```

Available version
:   66.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "swapStartDate": "2025-12-01T00:00:00Z",
          "outputRecordType": "Quote",
          "swapGroups": {
            "groups": [
              {
                "referenceId": "SWAP-001",
                "outGroup": {
                  "swapAssets": [
                    {
                      "assetId": "02ixx0000004HOAAA2",
                      "quantity": 1
                    }
                  ]
                },
                "inGroup": {
                  "graphId": "swapRequest",
                  "records": [
                    {
                      "referenceId": "refQuoteLine0",
                      "record": {
                        "attributes": {
                          "type": "QuoteLineItem",
                          "method": "POST"
                        },
                        "Product2Id": "01txx0000006iVlAAI",
                        "PricebookEntryId": "01uxx0000008ym4AAA",
                        "UnitPrice": 1049,
                        "Quantity": "1",
                        "StartDate": "2022-09-22"
                      }
                    }
                  ]
                }
              }
            ]
          }
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `contractId` | String | ID of the contract record to swap. | Optional | 66.0 |
        | `opportunityId` | String | ID of the opportunity record to swap. | Optional | 66.0 |
        | `outputRecordType` | String | Record type of the output for the swap. | Required | 66.0 |
        | `swapGroups` | [Swap Group](./connect_requests_swap_group.htm.md "Input representation of the details of the swap groupings for swap operations.")[] | Groups that contain the asset details for the swap. | Required | 66.0 |
        | `swapStartDate` | String | Amendment start date for the swap action. | Required | 66.0 |

Response body for POST
:   [Initiate Swap Response](./connect_responses_initiate_swap_output.htm.md "Output representation of the request to initiate a swap action.")

#### See Also

- [*Salesforce Help*: Swap, Upgrade, or Downgrade Assets](https://help.salesforce.com/s/articleView?id=ind.qocal_swap_upgrade_downgrade_amendments.htm&language=en_US "Salesforce Help: Swap, Upgrade, or Downgrade Assets - HTML (New Window)")
