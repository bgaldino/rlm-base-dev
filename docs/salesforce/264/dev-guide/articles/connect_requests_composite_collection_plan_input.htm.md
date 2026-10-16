---
page_id: connect_requests_composite_collection_plan_input.htm
title: Composite Collection Plan Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_composite_collection_plan_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-09-29
---

# Composite Collection Plan Input

Input representation of one or more collection plans, each with its
      optional nested collection plan items.

    

## JSON Example

      
      

```
{
  "collectionPlans": [
    {
      "accountId": "001xx000003DGXYA2",
      "contactId": "003xx000004TXYZA1",
      "initialDueAmount": 7500.00,
      "collectionPlanSegment": "High Risk",
      "dueDate": "2026-06-15",
      "collectionPlanReasonId": "0cR000000000001",
      "usageType": "Billing",
      "overdueRiskIndicator": "High",
      "collectionPlanItems": [
        {
          "invoiceId": "inv000000000001"
        },
        {
          "invoiceId": "inv000000000002"
        }
      ]
    }
  ]
}
```

    

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `collection​Plans` | [Collection Plan Input](./connect_requests_collection_plan_input.htm.md)[] | List of collection plans to create. Each plan can include a nested list of collection plan items to create with it. Specify at least 1 collection plan. | Required | 68.0 |
