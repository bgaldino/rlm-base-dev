---
page_id: connect_responses_api_execution_log.htm
title: API Execution Log Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_api_execution_log.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# API Execution Log Response

Output representation of the execution log of a pricing waterfall request.

    
      
        
          

**JSON example**

          
: 
            

```

{
  "message": {The Pricing API execution was successful.},
  "pricingElement": {
    "adjustments": [
      {
        "adjustmentType": null,
        "adjustmentValue": null
      }
    ],
    "name": "List Price",
    "elementType": "ListPrice"
  }
}
```

          

        
      

      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `message` | String [] | Message of the API execution. | Small, 63.0 | 63.0 |
| `pricingElement` | [Adjustment Details](./connect_responses_adjustment_detail.htm.md) | Details of the price adjustment of a pricing element. | Small, 63.0 | 63.0 |
