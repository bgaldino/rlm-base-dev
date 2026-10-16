---
page_id: connect_responses_category_output.htm
title: Category Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_category_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Category Output

Output representation of the category definition.

      
        
          

**JSON example**

          
: 
            

```
"categories": [
    {
      "catalogId": "0ZS1Q000000XbZAWA0",
      "code": "B2B Category",
      "description": "Products Category",
      "hasSubCategories": true,
      "id": "0ZG1Q000000XbVGWA0",
      "name": "Unified Computing",
      "numberOfProducts": 2,
      "parentCategoryId": "0ZGT100000000qlOAA",
      "sortOrder": 2,
      "subCategories": [],
      "isNavigational: false
    }
  ]
```

          

        
      

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
            
              

              

              

              

              

            

            
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `catalogId` | String | ID of the catalog that the category is associated with. | Small, 60.0 | 60.0 |
| `code` | String | Unique code of the product category. | Small, 60.0 | 60.0 |
| `description` | String | Description of the category. If data translation is set up and specified in the org, the translated description is available. | Small, 60.0 | 60.0 |
| `hasSub​Categories` | Boolean | Indicates whether the subcategories are available (true) or not (false). | Small, 60.0 | 60.0 |
| `id` | String | ID of the category. | Small, 60.0 | 60.0 |
| `isNavigational` | Boolean | Indicates whether the category node is navigational (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `name` | String | Name of the category. If data translation is set up and specified in the org, the translated name is available. | Small, 60.0 | 60.0 |
| `numberOf​Products` | Integer | Number of products associated with the category. | Small, 60.0 | 60.0 |
| `parent​CategoryId` | String | ID of the parent category. | Small, 60.0 | 60.0 |
| `sort​Order` | Integer | Display order of the product category relative to the siblings with the same parent category. | Small, 60.0 | 60.0 |
| `sub​Categories` | [Category Output](#)[] | List of subcategories, if available. This property is returned with the [Categories List (GET) API](./connect_resources_get_categories.htm.md) response. | Small, 60.0 | 60.0 |
