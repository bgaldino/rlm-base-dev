---
page_id: connect_responses_composite_collection_plan_output.htm
title: Composite Collection Plan
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_composite_collection_plan_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-09-29
---

# Composite Collection Plan

Output representation of the results for each collection
    plan.

    

## JSON Example

      
      

```
{
  "results": [
    {
      "collectionPlanId": "1Eu000000000001AAA",
      "collectionPlanItemIds": [
        "1Ev000000000001AAA",
        "1Ev000000000002AAA"
      ],
      "isSuccess": true,
      "errors": null
    }
  ]
}
```

    

    
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `results` | [Collection Plan](./connect_responses_collection_plan_output.htm.md)[] | List of results, with one result for each collection plan in the request. | Big, 68.0 | 68.0 |
