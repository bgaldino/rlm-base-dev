---
page_id: connect_resources_pricing_data_sync.htm
title: Pricing Data Sync (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_pricing_data_sync.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_business_apis_rest_references.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Pricing Data Sync (GET)

Sync pricing data to ensure that the lookup tables contain the
      latest pricing data.

    

To partially synchronize pricing data, use the Decision Table Refresh Action in a
        Flow. See [Decision Table Refresh
        Action](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/dt_actions_refresh_decision_table.htm).

        
          

**Resource**

          
: 
            

```
/connect/core-pricing/sync/pricingSyncOrigin
```

          

        
        
          

**Resource example**

          
: 

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/sync/syncData
```

This
            example shows a sample resource to filter by pricing
            recipe.

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/sync/syncData?pricingRecipeId=12Gxx0000005IzhEAE

```

        
        
          

**Available version**

          
: 60.0

        
        
          

**HTTP methods**

          
: GET

        
        
          

**Request parameters for GET**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `pricing​RecipeId` | String | ID of the pricing recipe whose decision tables you want to sync. If not specified, the default pricing recipe is used. | Optional | 67.0 |

          

        
        
          

**Response body for GET**

          
: [Pricing Generic
            Response](./connect_responses_pricing_generic_response.htm.md)
