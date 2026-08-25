---
page_id: connect_resources_initiate_downgrade.htm
title: Initiate Downgrade (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_initiate_downgrade.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_business_apis_rest_references.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Initiate Downgrade (POST)

Move to a lower-tier or lower-value product. The change is tracked as a
      downgrade request with linked asset actions and quote or order line linkage for reporting and
      auditing. This API creates an amendment quote and order with downgrade-specific order actions
      and quote action subtypes.

      

After assetization, the original asset receives an asset action with business category as
        Downgrade (or equivalent). This step indicates that the downgrade-from product and the new
        asset is created with an asset action (downgraded to), with relationships between the two.
        This step also enables sales reps to process downgrades and makes sure that downgrades are
        auditable and reportable separately from cancellations and new sales.

**Resource**

: 

```
/revenue/transaction-management/assets/actions/downgrade
```

**Resource example**

: 

```
https://yourInstance.salesforce.com/services/data/v68.0/revenue/transaction-management/assets/actions/downgrade
```

**Available version**

: 66.0

**HTTP methods**

: POST

**Request body for POST**

: 

**JSON example**

: 

```
{
  "swapStartDate": "2025-12-01T00:00:00Z",
  "outputRecordType": "Quote",
  "swapGroups": {
    "groups": [
      {
        "referenceId": "DOWNGRADE-001",
        "outGroup": {
          "swapAssets": [
            {
              "assetId": "02ixx0000004HOAAA2",
              "quantity": 1
            }
          ]
        },
        "inGroup": {
          "graphId": "downgradeRequest",
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

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contractId` | String | ID of the contract record to downgrade. | Optional | 66.0 |
| `opportunityId` | String | ID of the opportunity record to downgrade. | Optional | 66.0 |
| `outputRecordType` | String | Record type of the output for the downgrade. | Required | 66.0 |
| `swapGroups` | [Swap Group](./connect_requests_swap_group.htm.md)[] | Groups that contain the asset details for the downgrade. | Required | 66.0 |
| `swapStartDate` | String | Amendment start date for the downgrade action. | Required | 66.0 |

          

        

**Response body for POST**

: [Initiate Downgrade Response](./connect_responses_initiate_downgrade_output.htm.md)

#### See Also

- [*Salesforce Help*: Swap, Upgrade, or Downgrade Assets](https://help.salesforce.com/s/articleView?id=ind.qocal_swap_upgrade_downgrade_amendments.htm&language=en_US)
