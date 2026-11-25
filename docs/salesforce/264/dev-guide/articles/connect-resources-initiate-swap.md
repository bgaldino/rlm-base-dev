---
page_id: connect-resources-initiate-swap
title: Initiate Swap (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-initiate-swap.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-business-apis-rest-references
legacy_page_id: connect_resources_initiate_swap.htm
fetched_at: 2026-11-25
---

# Initiate Swap (POST)

Exchange one product for another of equivalent or different value. The change is tracked as a swap request with linked asset actions and a net-zero order total where applicable. The API creates an amendment quote and order with order actions and quote action subtypes.

When the order is assetized, the source asset gets an asset action with business category as `Swap` (reduced quantity). The new asset is created with an asset action that identifies it as swapped in, with relationships that link the swapped-from and swapped-to assets. The swaps are auditable and reportable separately from cancellations and new sales. This API also supports use cases such as trading unused licenses for credits or moving spend between products while preserving contract intent.

## Resource

```
/revenue/transaction-management/assets/actions/swap
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/revenue/transaction-management/assets/actions/swap
```

## Available Version

66.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

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

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contractId` | String | ID of the contract record to swap. | Optional | 66.0 |
| `opportunityId` | String | ID of the opportunity record to swap. | Optional | 66.0 |
| `outputRecordType` | String | Record type of the output for the swap. | Required | 66.0 |
| `swapGroups` | [Swap Group](./connect-requests-swap-group.md)[] | Groups that contain the asset details for the swap. | Required | 66.0 |
| `swapStartDate` | String | Amendment start date for the swap action. | Required | 66.0 |

## Response Body for POST

[Initiate Swap Response](./connect-responses-initiate-swap-output.md)

**See Also**

- [*Salesforce Help*: Swap, Upgrade, or Downgrade Assets](https://help.salesforce.com/s/articleView?id=ind.qocal_swap_upgrade_downgrade_amendments.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-initiate-swap.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
