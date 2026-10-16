---
page_id: connect_responses_product_selling_model_output.htm
title: Product Selling Model
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_selling_model_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Product Selling Model

Output representation of the definition of the product selling model.

      
        
          

**JSON example**

          
: 
            

```
"productSellingModel": 
{
  "id": "0jPT10000004CAfMAM",
  "name": "OneTimePSM",
  "pricingTerm": 1,
  "pricingTermUnit": "Months",
  "sellingModelType": "TermDefined",
  "status": "Active"
}
}]
```

          

        
      

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              
- 
- 
- 

              

              

            

            
              

              

              

              

              

            

          

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the record. | Small, 60.0 | 60.0 |
| `name` | String | Name of the record. | Small, 60.0 | 60.0 |
| `pricing​Term` | Integer | Duration of the selling model. | Small, 60.0 | 60.0 |
| `pricing​Term​Unit` | String | Units of the pricing term. | Small, 60.0 | 60.0 |
| `selling​Model​Type` | String | Different models of selling the product. Valid values are: `OneTime` `TermDefined` `Evergreen` | Small, 60.0 | 60.0 |
| `status` | String | Status of the selling model. For example, whether the selling model is active and can be used in transactions. | Small, 60.0 | 60.0 |
