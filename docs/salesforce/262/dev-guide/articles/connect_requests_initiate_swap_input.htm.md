---
page_id: connect_requests_initiate_swap_input.htm
title: Initiate Swap Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_initiate_swap_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-06-09
---

# Initiate Swap Input

Input representation of the details of the request to initiate a swap action.

JSON example
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
