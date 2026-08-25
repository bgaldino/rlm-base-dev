---
page_id: connect_responses_pricing_recipe_look_up_table_response.htm
title: Pricing Recipe LookUp Table Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_pricing_recipe_look_up_table_response.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Pricing Recipe LookUp Table Response

Output representation of a pricing recipe lookup table.

      
        
          

**JSON example**

          
: 
            

```

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
      ]
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the pricing recipe table mapping. | Small, 60.0 | 60.0 |
| `is​Internal` | Boolean | Indicates if the decision table is available (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `pricing​Component​Type` | String | Price component types such as, custom discount, volume discount, attribute-based discount, bundle-based discount, and list price. | Small, 60.0 | 60.0 |
