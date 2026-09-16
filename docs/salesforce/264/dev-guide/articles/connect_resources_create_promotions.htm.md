---
page_id: connect_resources_create_promotions.htm
title: Create Promotions (GET, POST, PUT)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_create_promotions.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_business_apis_rest_references.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Create Promotions (GET, POST, PUT)

Get rewards based on a product selling model
    template.

    
      
        
          

**Resource**

          
: 
            

```
/global-promotions-management/promotions
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/global-promotions-management/promotions
```

          

        
        
          

**Available version**

          
: 66.0

        
        
          

**HTTP methods**

          
: GET, POST, PUT

        
        
          

**Request and response body**

          
: This example shows a sample request to create a
            promotion.

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

          
: See [Promotions Creation API](https://developer.salesforce.com/docs/atlas.en-us.264.0.loyalty.meta/loyalty/connect_resources_unified_promotions.htm)
            reference to get additional details of the request and response properties.
