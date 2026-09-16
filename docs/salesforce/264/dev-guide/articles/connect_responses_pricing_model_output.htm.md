---
page_id: connect_responses_pricing_model_output.htm
title: Pricing Model
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_pricing_model_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Pricing Model

Output representation of the details of the pricing model.

        
          

**JSON example**

          
: 
            

```
{
  "pricingModel": {
    "id": "0jPSG000000Avcv2AC",
    "name": "One Time",
    "pricingModelType": "OneTime"
  }
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `frequency` | String | Details about the frequency of recurrence of the pricing model. | Small, 67.0 | 67.0 |
| `id` | String | ID of the pricing model. | Small, 67.0 | 67.0 |
| `name` | String | Name of the pricing model. | Small, 67.0 | 67.0 |
| `occurrence` | Integer | Details about the number of occurrences of the pricing model. | Small, 67.0 | 67.0 |
| `pricingModelType` | String | Type of the pricing model. | Small, 67.0 | 67.0 |
| `unitOfMeasure` | String | Unit of measure for the pricing model. | Small, 67.0 | 67.0 |
