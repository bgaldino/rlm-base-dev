---
page_id: connect_requests_collection_plan_item_input.htm
title: Collection Plan Item Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_collection_plan_item_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-09-29
---

# Collection
    Plan Item Input

Input representation of a single collection plan item to create under
      a collection plan.

    

## JSON Example

      
      

```
{
  "collectionPlanId": "1Eu000000000001AAA",
  "invoiceId": "inv000000000001"
}
```

    

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `collection​PlanId` | String | ID of the collection plan that the item belongs to. When the item is nested within a collection plan in the same request, this property defaults to the parent collection plan. | Optional | 68.0 |
| `invoiceId` | String | ID of the invoice associated with the collection plan item. The invoice must have a status of `Posted` and a settlement status other than `Settled`. All invoices associated with a collection plan must use the same currency. | Required only if `collectionPlanItems` is present | 68.0 |
