---
page_id: connect-requests-initiate-swap-input
title: Initiate Swap Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-initiate-swap-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-requests
legacy_page_id: connect_requests_initiate_swap_input.htm
fetched_at: 2026-11-25
---

# Initiate Swap Input

Input representation of the details of the request to initiate a swap action.

## JSON Example

```
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

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contractId` | String | ID of the contract record to swap. | Optional | 66.0 |
| `opportunityId` | String | ID of the opportunity record to swap. | Optional | 66.0 |
| `outputRecordType` | String | Record type of the output for the swap. | Required | 66.0 |
| `swapGroups` | [Swap Group](./connect-requests-swap-group.md)[] | Groups that contain the asset details for the swap. | Required | 66.0 |
| `swapStartDate` | String | Amendment start date for the swap action. | Required | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-initiate-swap-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
