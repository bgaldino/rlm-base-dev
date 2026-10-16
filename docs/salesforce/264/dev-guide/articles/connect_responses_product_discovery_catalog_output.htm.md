---
page_id: connect_responses_product_discovery_catalog_output.htm
title: Catalog Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_discovery_catalog_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Catalog Details

Output representation of the details of a catalog definition.

    
      
        
          

**JSON example**

          
: 
            

```
{
  "catalogs": [
    {
      "customFields": {},
      "id": "0ZSSG000001875O4AQ",
      "name": "Hardware Catalog",
      "numberOfCategories": 4
    }
  ]
}
```

          

        
      

      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `catalogCode` | String | Unique ID associated with the catalog. | Small, 67.0 | 67.0 |
| `catalogType` | String | Category of an entry in the catalog, which is customizable. For example, catalog types, such as sellable products, services, parts, technical services, or technical resources. | Small, 67.0 | 67.0 |
| `customFields` | Map<String, Object> | Details of the custom fields associated with a catalog. | Small, 67.0 | 67.0 |
| `description` | String | Description of the catalog. | Small, 67.0 | 67.0 |
| `effectiveEndDate` | String | Date and time from when the catalog isn’t available to the end users. | Small, 67.0 | 67.0 |
| `effectiveStartDate` | String | Date and time from when the catalog is available to the end users. | Small, 67.0 | 67.0 |
| `id` | String | ID of the catalog. | Small, 67.0 | 67.0 |
| `name` | String | Name of the catalog. | Small, 67.0 | 67.0 |
| `numberOfCategories` | Integer | Number of categories in the catalog. | Small, 67.0 | 67.0 |
| `status` | String | Status of the catalog. | Small, 67.0 | 67.0 |
