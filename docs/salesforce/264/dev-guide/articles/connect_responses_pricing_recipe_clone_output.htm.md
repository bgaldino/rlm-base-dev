---
page_id: connect_responses_pricing_recipe_clone_output.htm
title: Pricing Recipe Clone
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_pricing_recipe_clone_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-09-29
---

# Pricing Recipe Clone

Output representation of the payload for the pricing recipe clone operation.

    

## JSON Example

      
      

```

{
    "isSuccess" : true,
    "newPricingRecipeId" : "0ClxX0000004D1AACU",
    "newPricingRecipeName" : "Cloned Recipe"
}

```

    

    
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | [Pricing Recipe Clone Error](./connect_responses_pricing_recipe_clone_error.htm.md) | Details of the error encountered during the clone operation, if any. | Big, 68.0 | 68.0 |
| `isSuccess` | Boolean | Indicates whether the clone operation was successful (`true`) or not (`false`). | Big, 68.0 | 68.0 |
| `new​Pricing​RecipeId` | String | ID of the cloned pricing recipe. | Big, 68.0 | 68.0 |
| `new​Pricing​RecipeName` | String | Name of the cloned pricing recipe. | Big, 68.0 | 68.0 |
