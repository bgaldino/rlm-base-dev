---
page_id: connect_responses_index_configuration_field_output.htm
title: Index Configuration Field
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_index_configuration_field_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Index Configuration Field

Output representation of the details of the index-configured field.

        
          

**JSON example**

          
: 
            

```
  "indexConfigurations": [
    {
      "attributeDefinitionId": "0tjT1000000002bIAA",
      "name": "Color",
      "type": "ProductDynamicAttribute",
      "isSearchable": true
    },
    {
      "attributeFieldId": "00Nxx000001FwnABII",
      "name": "Message__c",
      "type": "Custom",
      "isSearchable": true
    },
    {
      "name": "Code",
      "type": "Standard",
      "isSearchable": true
    },
    {
      "facetDisplayRank": 1,
      "isFacetable": false,
      "isSearchable": true,
      "name": "Family",
      "type": "Standard"
    }
  ]
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `attribute​DefinitionId` | String | ID of the attribute definition. | Small, 62.0 | 62.0 |
| `attribute​FieldId` | String | ID of the attribute field. | Small, 62.0 | 62.0 |
| `facetDisplay​Rank` | Integer | Sort order for displaying the facets at run time. | Small, 63.0 | 63.0 |
| `is​Facetable` | Boolean | Indicates whether the field is facetable (`true`) or not (`false`). | Small, 63.0 | 63.0 |
| `is​Searchable` | Boolean | Indicates whether the index-configured field is searchable (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `name` | String | Name of the index-configured field. | Small, 62.0 | 62.0 |
| `type` | String | Type of the index-configured field. | Small, 62.0 | 62.0 |
