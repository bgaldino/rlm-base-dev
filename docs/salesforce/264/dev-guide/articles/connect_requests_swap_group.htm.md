---
page_id: connect_requests_swap_group.htm
title: Swap Group Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_swap_group.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-11-23
---

# Swap Group Input

Input representation of the details of the swap groupings for swap operations.

## JSON Example

```
{
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

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `inGroup` | Object | Products to include in the swap. These objects are supported. QuoteLineItem or OrderItem. | Required | 66.0 |
| `outGroup` | [Swap Group](# "Input representation of the details of the swap groupings for swap operations.")[] | Assets to exclude from the swap. You can’t use string values for properties, such as quantity and price. | Required | 66.0 |
| `referenceId` | String | Reference ID of the operation. | Required | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_swap_group.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
