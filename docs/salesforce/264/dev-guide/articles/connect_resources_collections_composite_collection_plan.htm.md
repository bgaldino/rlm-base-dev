---
page_id: connect_resources_collections_composite_collection_plan.htm
title: Composite Collection Plan Creation (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_collections_composite_collection_plan.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-09-29
---

# Composite Collection Plan Creation (POST)

Create one or more collection plans, each with its collection plan
      items, in a single request.

    
      

This API creates each collection plan in the request together with its nested collection
        plan items. Each collection plan runs independently, so the request can partially succeed
        across plans. Within a single collection plan, if any of its collection plan items fail to
        create, the parent collection plan is rolled back. The response returns a result for each
        collection plan in the request that indicates whether the collection plan was created
        successfully and includes any errors.

    

    

## Special Access Rules

      
      

Set up collections and enable invoicing in your org.

    

    

## Resource

      
      

```
/connect/collections/composite-collection-plan
```

    

    

## Resource Example

      
      

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/collections/composite-collection-plan
```

    

    

## Available Version

      
      

68.0

    

    

## HTTP Methods

      
      

POST

    

    

## Request Body for POST

      
      

**JSON Example**

      

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

      

**Properties**

      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `collection​Plans` | [Collection Plan Input](./connect_requests_collection_plan_input.htm.md)[] | List of collection plans to create. Each plan can include a nested list of collection plan items to create with it. Specify at least 1 collection plan. | Required | 68.0 |

    

    

## Response Body for POST

      
      

[Composite
          Collection Plan](./connect_responses_composite_collection_plan_output.htm.md)
