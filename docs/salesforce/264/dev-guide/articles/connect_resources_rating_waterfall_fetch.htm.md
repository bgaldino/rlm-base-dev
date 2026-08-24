---
page_id: connect_resources_rating_waterfall_fetch.htm
title: Rating Waterfall (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_rating_waterfall_fetch.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Rate Management
parent_page: rate_management_business_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Rating Waterfall (GET)

Get the persisted rating waterfall that stores the process logs.
      Rating waterfall provides insights into the internal rating process.

    
      
        
          

**Resource**

          
: 
            

```
/connect/core-pricing/waterfall/lineItemId/executionId
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/waterfall/Gold/2yHdNNEFOZr9jAe4gHS7?tagsToFilter=UnitPrice&usageType=Rating
```

          

        
        
          

**Available version**

          
: 62.0

        
        
          

**HTTP methods**

          
: GET

        
        
          

**Query parameters**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

- 
- 

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `tagsTo​Filter` | String | Comma-separated tags to filter. | Optional | 62.0 |
| `usage​Type` | String | Usage type of the waterfall log record. Valid values are: `Rating` `Pricing`—Specifies that the record type is `Pricing`. If this value is specified, the API creates a log of pricing waterfall. See [Pricing Waterfall](./connect_resources_pricing_waterfall_post.htm.md). The default value is `Pricing`. | Optional | 62.0 |

          

        
        
          

**Response body for GET**

          
: [Line Item Waterfall
            Response](./connect_responses_rating_line_item_waterfall_response.htm.md)
