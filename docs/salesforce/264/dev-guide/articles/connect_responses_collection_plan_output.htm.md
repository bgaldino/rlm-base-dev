---
page_id: connect_responses_collection_plan_output.htm
title: Collection Plan
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_collection_plan_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-09-29
---

# Collection Plan

Output representation of the result of a single collection plan
      creation request.

    

## JSON Example

      
      

```
{
  "collectionPlanId": "1Eu000000000001AAA",
  "collectionPlanItemIds": [
    "1Ev000000000001AAA",
    "1Ev000000000002AAA"
  ],
  "isSuccess": true,
  "errors": null
}
```

    

    
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `collection​PlanId` | String | ID of the created collection plan. This value is null if the creation failed. | Big, 68.0 | 68.0 |
| `collection​Plan​ItemIds` | String[] | IDs of the created collection plan items. This value is null if the creation failed. | Big, 68.0 | 68.0 |
| `errors` | [Collection Plan Error](./connect_responses_collection_plan_error.htm.md)[] | List of errors that occurred while creating the collection plan. This value is null if the creation succeeded. | Big, 68.0 | 68.0 |
| `isSuccess` | Boolean | Indicates whether collection plan creation was successful (`true`) or not (`false`). | Big, 68.0 | 68.0 |
