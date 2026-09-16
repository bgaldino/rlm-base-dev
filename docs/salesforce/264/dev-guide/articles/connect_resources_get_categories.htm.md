---
page_id: connect_resources_get_categories.htm
title: Categories List (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_categories.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Categories List (GET)

Retrieve the root-level categories of a catalog based
      on a catalog ID, or subcategories based on a parent category. You can also search, filter, or
      sort the categories.

    
      
        
          

**Resource**

          
: 
            

```
/connect/pcm/catalogs/catalogId/categories
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/catalogs/0ZST100000000kUOAQ/categories
```

            

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/catalogs/0ZST100000000kUOAQ/categories?language=spanish
```

          

        
        
          

**Available version**

          
: 60.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
: GET

        
        
          

**Request parameters for GET**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Optional | 60.0 |
| `depth` | Integer | Number of levels in the category hierarchy to return. The default value is 1. | Optional | 60.0 |
| `fields` | String[] | For internal use only. | Optional | 60.0 |
| `language` | String | Custom language that you can specify to get translated data for the fields of an object that's enabled for translation. See [Translate Product and Product Category Data](https://help.salesforce.com/s/articleView?id=ind.product_catalog_translate_product2_and_productcategory_data.htm&language=en_US). | Optional | 64.0 |
| `parent​Category​Id` | String | ID of the category to fetch the associated hierarchy of subcategories. If unspecified, then the root-level categories are returned. | Optional | 60.0 |

          

        
        
          

**Response body for GET**

          
: [Categories Output](./connect_responses_categories_output.htm.md)
