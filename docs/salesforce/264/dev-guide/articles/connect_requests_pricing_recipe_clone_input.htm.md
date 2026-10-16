---
page_id: connect_requests_pricing_recipe_clone_input.htm
title: Pricing Recipe Clone Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_pricing_recipe_clone_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_requests.htm
fetched_at: 2026-09-29
---

# Pricing Recipe Clone Input

Input representation to clone a pricing recipe.

    

## JSON Example

      
      

```

{
    "recordId" : "0ClxX0000004CxWACU",
    "newPricingRecipeApiName" : "Cloned_Recipe",
    "newPricingRecipeName" : "Cloned Recipe",
    "pricingUsageSubType" : "Loyalty"
}

```

    

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `new​Pricing​Recipe​ApiName` | String | API name of the cloned pricing recipe. | Required | 68.0 |
| `new​Pricing​Recipe​Name` | String | Name for the cloned pricing recipe. | Required | 68.0 |
| `pricing​Usage​SubType` | String | Pricing usage subtype of the cloned pricing recipe. If unspecified, the value from the source pricing recipe is used. | Optional | 68.0 |
| `recordId` | String | ID of the source pricing recipe to clone. | Required | 68.0 |
