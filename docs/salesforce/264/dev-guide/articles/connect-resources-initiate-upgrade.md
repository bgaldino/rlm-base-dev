---
page_id: connect-resources-initiate-upgrade
title: Initiate Upgrade (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-initiate-upgrade.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-business-apis-rest-references
legacy_page_id: connect_resources_initiate_upgrade.htm
fetched_at: 2026-11-25
---

# Initiate Upgrade (POST)

Move a lower-tier product to a higher-tier product. The change is tracked as an upgrade request with linked asset actions and quote or order line linkage for reporting and auditing. This API creates an amendment quote and order with order actions and quote action subtypes.

The original asset receives an asset action with an `Upgrade` (or equivalent) business category. This step indicates that the upgrade-from product and the new asset is created with an asset action (upgraded to), with relationships between the two. This step also enables sales reps to process upgrades and makes sure that upgrades are distinguishable in reporting and analytics from cancellations plus new sales.

## Resource

```
/revenue/transaction-management/assets/actions/upgrade
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/revenue/transaction-management/assets/actions/upgrade
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

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contractId` | String | ID of the contract record to upgrade. | Optional | 66.0 |
| `opportunityId` | String | ID of the opportunity record to upgrade. | Optional | 66.0 |
| `outputRecordType` | String | Record type of the output for the upgrade. | Required | 66.0 |
| `swapGroups` | [Swap Group](./connect-requests-swap-group.md)[] | Groups that contain the asset details for the upgrade. | Required | 66.0 |
| `swapStartDate` | String | Amendment start date for the upgrade action. | Required | 66.0 |

## Response Body for POST

[Initiate Upgrade Response](./connect-responses-initiate-upgrade-output.md)

**See Also**

- [*Salesforce Help*: Swap, Upgrade, or Downgrade Assets](https://help.salesforce.com/s/articleView?id=ind.qocal_swap_upgrade_downgrade_amendments.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-initiate-upgrade.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
