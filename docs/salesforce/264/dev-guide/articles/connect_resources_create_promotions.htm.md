---
page_id: connect_resources_create_promotions.htm
title: Create Promotions (GET, POST, PUT)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_create_promotions.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_business_apis_rest_references.htm
fetched_at: 2026-11-23
---

# Create Promotions (GET, POST, PUT)

Get rewards based on a product selling model template.

## Resource

```
/global-promotions-management/promotions
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/global-promotions-management/promotions
```

## Available Version

66.0

## HTTP Methods

GET, POST, PUT

## Request and Response Body

This example shows a sample request to create a promotion.

```
{
  "promotionDetails": {
    "additionalFieldValues": {
      "attributes": {}
    },
    "displayName": "10% off on Cisco Router",
    "isAutomatic": true,
    "isEmailActivated": false,
    "name": "10% off on Cisco Router",
    "promotionEligibility": {
      "eligibleCustomerEvents": {},
      "eligibleEnrollmentPeriod": {
        "isEnrollmentRequired": false
      },
      "eligibleProducts": [
        {
          "id": "01txx0000006igmAAA",
          "name": "Cisco Router",
          "productType": "SimpleProduct"
        }
      ]
    },
    "promotionLimits": {},
    "ruleLibrary": {
      "id": "9Qsxx0000004H76CAE",
      "name": "RLMSales"
    },
    "startDateTime": "2025-11-01T08:43:00.000Z"
  },
  "rules": [
    {
      "eventConfiguration": [],
      "journalSubType": null,
      "journalSubTypeName": null,
      "journalType": "Customer Purchase",
      "priority": 10,
      "rewardConfiguration": [
        {
          "scope": "SimpleProduct",
          "scopeDetails": [
            {
              "name": "Cisco Router",
              "id": "01txx0000006igmAAA"
            }
          ],
          "doNotDefineRewards": false,
          "rewardDetailsList": [
            {
              "productSellingModel": {
                "name": "Monthly",
                "id": "0jPxx0000000001EAA"
              },
              "discountType": "PercentageOff",
              "discountValue": 10,
              "termBasedRewards": {
                "psmTenure": {
                  "tenure": "SpecificTerm",
                  "operator": "Equals",
                  "value": 12
                },
                "rewardDuration": {
                  "tenure": "SpecificTerm",
                  "value": 3
                }
              }
            }
          ],
          "childProducts": [],
          "type": "PSMDiscount",
          "isPrimaryReward": false
        }
      ],
      "ruleName": "rule",
      "templateName": "GetRewardsBasedOnSellingModel"
    }
  ]
}
```

See [Promotions Creation API](https://developer.salesforce.com/docs/atlas.en-us.264.0.loyalty.meta/loyalty/connect_resources_unified_promotions.htm "HTML (New Window)") reference to get additional details of the request and response properties.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_create_promotions.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
