---
page_id: connect_responses_billing_arrangement_output.htm
title: Billing Arrangement
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_billing_arrangement_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Billing Arrangement

Output representation that contains the details of a billing arrangement, including its
    status, configuration settings, and associated lines.

        
          

**JSON example**

          
: 
            

```
{
  "billingArrangementId": "1bdxx000000004rAAA",
  "name": "Acme Shared Billing Definition",
  "isAdjustmentToOwnAccount": true,
  "remainderPercentage": 15,
  "versionNumber": 1,
  "numOfAssociatedBSGs": 5,
  "status": "Active",
  "billingArrangementLines": [
    {
      "billingArrangementLineId": "1blxx000000006TAAQ",
      "accountId": "accId1",
      "billingAccountId": "bAccId1",
      "isRemainderAdjustmentAccount": false,
      "percentage": 60
    },
    {
      "billingArrangementLineId": "1blxx000000001dAAA",
      "accountId": "accId2",
      "billingAccountId": "bAccId2",
      "isRemainderAdjustmentAccount": false,
      "percentage": 25
    }
  ],
  "isSuccess": true,
  "error": null
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              
- 
- 
- 

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `billing​ArrangementId` | String | Unique ID of the billing arrangement. | Big, 66.0 | 66.0 |
| `billing​ArrangementLines` | [Billing Arrangement Line](./connect_responses_billing_arrangement_line.htm.md)[] | List of billing arrangement lines associated with the latest version of the billing arrangement. | Big, 66.0 | 66.0 |
| `error` | [Error Response Output](https://developer.salesforce.com/docs/atlas.en-us.264.0.chatterapi.meta/chatterapi/connect_responses_error_response.htm) | Error details if the request was unsuccessful. | Big, 66.0 | 66.0 |
| `isAdjustment​ToOwnAccount` | Boolean | Indicates whether the remainder of the bill is adjusted to the owning account (`true`) or not (`false`). | Big, 66.0 | 66.0 |
| `isSuccess` | Boolean | Indicates whether the request was successfully processed (`true`) or not (`false`). | Big, 66.0 | 66.0 |
| `name` | String | Name of the billing arrangement. | Big, 66.0 | 66.0 |
| `numOf​AssociatedBSGs` | Integer | Total number of billing schedule groups associated with the billing arrangement. | Big, 66.0 | 66.0 |
| `remainderPercentage` | Double | Remaining percentage of the bill after all line allocations are calculated. | Big, 66.0 | 66.0 |
| `status` | String | Status of the billing arrangement. Valid values are: `Draft` `Active` `Inactive` | Big, 66.0 | 66.0 |
| `versionNumber` | Integer | Current version number of the billing arrangement. | Big, 66.0 | 66.0 |
