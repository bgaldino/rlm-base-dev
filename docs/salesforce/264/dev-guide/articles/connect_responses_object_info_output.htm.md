---
page_id: connect_responses_object_info_output.htm
title: Object Info
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_object_info_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Object Info

Output representation of the object details along with its fields.

        
          

**JSON example**

          
: 
            

```
    "objectInfos": [
      {
        "fields": [
          {
            "dataType": "text",
            "isFacetableConfigurable": true,
            "isSearchableConfigurable": false,
            "label": "Product Name",
            "name": "Name",
            "type": "Standard"
          },
          {
            "dataType": "multilinetext",
            "isFacetableConfigurable": false,
            "isSearchableConfigurable": true,
            "label": "Product Description",
            "name": "Description",
            "type": "Standard"
          }
        ],
        "name": "Product2"
      },
      {
        "fields": [
          {
            "dataType": "stringplusclob",
            "label": "Description",
            "name": "Description",
            "type": "ProductAttributeDefinitionStandard"
          },
          {
            "dataType": "text",
            "label": "Name",
            "name": "Name",
            "type": "ProductAttributeDefinitionStandard"
          },
        ],
        "name": "ProductAttributeDefinition"
      }
    ]
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `fields` | [Fields Info](./connect_responses_fields_info_output.htm.md)[] | Fields of the object. | Small, 62.0 | 62.0 |
| `name` | String | Name of the object. | Small, 62.0 | 62.0 |
