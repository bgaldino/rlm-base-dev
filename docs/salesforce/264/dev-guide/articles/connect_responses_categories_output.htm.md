---
page_id: connect_responses_categories_output.htm
title: Categories Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_categories_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Categories Output

Output representation of the retrieved categories result.

      
        
          

**JSON example**

          
: 
            

```
{
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
  ],
  "correlationId": "30230973-0a09-405e-b148-f085bb6dd66e",
  "status": {
    "code": "200",
    "errors": [],
    "message": "Successfully fetched the category records."
  }
}
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `categories` | [Category Output](./connect_responses_category_output.htm.md)[] | List of the retrieved categories. | Small, 60.0 | 60.0 |
| `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Small, 60.0 | 60.0 |
| `status` | [Status](./connect_responses_status.htm.md) | Status of the request. | Small, 60.0 | 60.0 |
