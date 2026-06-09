---
page_id: connect_requests_initiate_upgrade_input.htm
title: Initiate Upgrade Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_initiate_upgrade_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-06-09
---

# Initiate Upgrade Input

Input representation of the details of the request to initiate an upgrade action. The
response includes the ID of the sales transaction that the upgrade action creates.

JSON example
:   ```
    {
      "swapStartDate": "2025-12-01T00:00:00Z",
      "outputRecordType": "Quote",
      "swapGroups": {
        "groups": [
          {
            "referenceId": "UPGRADE-001",
            "outGroup": {
              "swapAssets": [
                {
                  "assetId": "02ixx0000004HOAAA2",
                  "quantity": 1
                }
              ]
            },
            "inGroup": {
              "graphId": "upgradeRequest",
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
                    "StartDate": "2026-03-22"
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
    | `contractId` | String | ID of the contract record to upgrade. | Optional | 66.0 |
    | `opportunityId` | String | ID of the opportunity record to upgrade. | Optional | 66.0 |
    | `outputRecordType` | String | Record type of the output for the upgrade. | Required | 66.0 |
    | `swapGroups` | [Swap Group](./connect_requests_swap_group.htm.md "Input representation of the details of the swap groupings for swap operations.")[] | Groups that contain the asset details for the upgrade. | Required | 66.0 |
    | `swapStartDate` | String | Amendment start date for the upgrade action. | Required | 66.0 |
