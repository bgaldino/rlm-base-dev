---
page_id: connect_resources_price_recipe_mapping.htm
title: Pricing Recipe Mapping (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_price_recipe_mapping.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_business_apis_rest_references.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Pricing Recipe Mapping (POST)

Create a mapping between the pricing recipe and the Decision Tables.
      Post recipes with lookup tables or procedures.

    
      
        
          

**Resource**

          
: 
            

```
/connect/core-pricing/recipe/mapping
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/recipe/mapping
```

          

        
        
          

**Available version**

          
: 60.0

        
        
          

**HTTP methods**

          
: POST

        
        
          

**Request body for POST**

          
: 
            

**JSON example**

: 

```

{
    "recipeId" : "12Gxx0000005J9MEAU",
    "pricingRecipeLookUpTableInputRepresentations": [
    {
      lookupId: “12Gxx0000005J9MEAU”, 
      pricingComponentType: “CustomDiscount”
  },
    {
      lookupId: “12Gxx0000005J9MEAU”, 
      pricingComponentType: “CustomDiscount”
  }
 ],
    "pricingRecipeProcedureInputRepresentation" : {
    "procedureId" : "9QLxx0000004C92GAE"
}
}

```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `pricing​RecipeLookUp​Table​Input​Representations` | [Pricing Recipe LookUp Table Input](./connect_requests_pricing_recipe_look_up_table_input.htm.md)[] | Input representation of the recipe mapping. | Required | 60.0 |
| `pricing​Recipe​Procedure​Input​Representation` | [Pricing Recipe Procedure Input](./connect_requests_pricing_recipe_procedure_input.htm.md) | Input representation of the procedure that’s used in the pricing recipe. | Required | 60.0 |
| `recipeId` | String | ID of the pricing recipe. | Required | 60.0 |

          

        
        
          

**Response body for POST**

          
: [Pricing Recipe
              Post](./connect_responses_pricing_recipe_post_output.htm.md)
