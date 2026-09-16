---
page_id: connect_resources_asset_usage_details.htm
title: Asset Usage Details (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_asset_usage_details.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Asset Usage Details (GET)

Get details of a usage-based product associated with an asset. This
      covers details of grants, resources, and configured rates for the product, including
      negotiated rates in case of a rate override.

    

Here are the details that this API returns.

        
- Grants and resources for the product, if rates aren’t configured.

        
- Grants, resources, and any configured rates for the product. The rates are returned by
          the [Rate Plan (GET) API](./connect_resources_get_rate_plan.htm.md).

        
- Resources that include grants, if applicable, and any negotiated rates for the product
          in case of a rate override request.

      

This API doesn't return binding target rates. Use the [Binding Object Usage Details
          API](./connect_resources_retrieve_binding_object_details.htm.md) to retrieve binding target rates.

    
      
        
          

**Resource**

          
: 
            

```
/asset-management/assets/assetId/usage-details
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/asset-management/assets/02iRM0000000tCdYAI/usage-details
```

          

        
        
          

**Available version**

          
: 63.0

        
        
          

**HTTP methods**

          
: GET

        
        
          

**Path parameter for GET**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `assetId` | String | ID of the asset. | Required | 63.0 |

          

        
        
          

**Query parameters for GET**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    
- 
- 

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `effectiveDate` | String | Date that's used to search for the applicable rate card entries. | Required | 63.0 |
| `optionalFields` | String[] | Custom fields that you can use to query these objects. [AssetRateCardEntry](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_assetratecardentry.htm) [AssetRateAdjustment](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_assetrateadjustment.htm) | Optional | 63.0 |

          

        
        
          

**Response body for GET**

          
: [Usage
            Details](./connect_responses_usage_detail_output.htm.md)
