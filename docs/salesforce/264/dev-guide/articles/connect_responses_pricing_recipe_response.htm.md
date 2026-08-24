---
page_id: connect_responses_pricing_recipe_response.htm
title: Pricing Recipe Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_pricing_recipe_response.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Pricing Recipe Response

Output representation of the pricing recipe.

      
        
          

**JSON example**

          
: 
            

```
{
  "recipes": [
    {
      "active": false,
      "createdBy": "autoproc@00dxx0000006gmjea2",
      "createdOn": "2023-07-15T13:12:38.000Z",
      "decisionTables": [
        {
          "id": "0lDxx00000000T3EAI",
          "isInternal": true,
          "pricingComponentType": "ListPrice"
        },
        {
          "id": "0lDxx00000000T4EAI",
          "isInternal": true,
          "pricingComponentType": "VolumeDiscount"
        },
        {
          "id": "0lDxx00000000HlEAI",
          "isInternal": false,
          "pricingComponentType": "CustomDiscount"
        }
      ],
      "developerName": "NGPDefaultRecipe",
      "id": "12Gxx0000005Ka4EAE",
      "name": "NGPDefaultRecipe",
      "procedureCreatedBy": "",
      "procedureCreatedOn": "2023-09-19T11:39:18.983Z",
      "procedureId": "",
      "procedureName": ""
    }],
  "success": true
}

```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `recipes` | [Pricing Recipe Output Representation](./connect_responses_pricing_recipe_output.htm.md)[] | Representation of the pricing recipe. | Small, 60.0 | 60.0 |
| `success` | Boolean | Indicates if the request is successful (`true`) or not (`false`). | Small, 60.0 | 60.0 |
