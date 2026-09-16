---
page_id: connect_requests_category_list_input.htm
title: Category List Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_category_list_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Category List Input

Input representation of the request to get a list of categories.

        
          

**JSON example**

          
: 

```
{
  "correlationId": "9cbb9650-48c5-11ed-96d1-0afcf185843b",
  "catalogId": "0ZSxx000000009hGAA",
  "userContext": {
      "accountId": "001xx0000000001AAA",
      "contactId": "003xx00000000D7AAI"
    }
}
```

This example shows a sample request to get a list of categories with eligible
            promotions.

```
{
  "correlationId": "9cbb9650-48c5-11ed-96d1-0afcf185843b",
  "catalogId": "0ZSxx000000009hGAA",
  "userContext": {
    "accountId": "001xx0000000001AAA",
    "contactId": "003xx00000000D7AAI"
  },
  "usePromotions": true
}
```

        
      

      
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

- 
- 
- 

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `additional​ContextData` | [Context Data Input](./connect_requests_context_data_input.htm.md)[] | Additional nodes that are added to the custom or default context definition. The maximum number of supported nodes is 10. | Optional | 60.0 |
| `catalog​Id` | String | ID of the catalog. | Required | 60.0 |
| `context​Definition` | String | API name of the custom context definition that’s sent for context creation. If this property isn’t specified, then the default context definition is used. | Optional | 60.0 |
| `context​Mapping` | String | Default context mapping of the context definition. If a context mapping is specified, then the API checks whether the mapping belongs to the specified context definition to process the details for hydration. | Optional | 60.0 |
| `correlation​Id` | String | Unique identifier value that’s attached to the requests and messages, and accepts references to a particular transaction or event chain. | Optional | 60.0 |
| `customFields` | String[] | List of additional custom fields to include in the response. | Optional | 60.0 |
| `depth` | Integer | Specifies the levels of subcategories to retrieve beneath the parent category. This parameter only applies when `parentCategoryId` is provided. | Optional | 61.0 |
| `enableQualification` | Boolean | Indicates whether to enable qualification rules for the products (`true`) or not (`false`). The default value is `true`. | Optional | 60.0 |
| `filter` | [Filter Input](./connect_requests_filter_input.htm.md) | Filters records based on supported criteria.The supported property is `isQualified`. The supported operators are: `eq` `in` `contains`—This value isn't applicable if the **Use Indexed Data For Product Listing and Search** toggle from the Product Discovery Settings page from Setup is enabled. | Optional | 62.0 |
| `parent​CategoryId` | String | ID of the parent category whose subcategories you want to retrieve. If not specified, only root-level categories from the catalog are returned. | Optional | 61.0 |
| `qualification​Procedure` | String | API name of the custom qualification procedure that’s used for the product qualification process. If this property isn’t specified, then the default qualification procedure is executed. | Optional | 60.0 |
| `usePromotions` | Boolean | Indicates whether to fetch eligible promotions from Global Promotion Management (GPM) for the requested category and its products (`true`) or not (`false`). If Promotion feature is enabled in the org and this property isn't specified, then the default value is `true`. If the Promotion feature isn't enabled, the default value is `false`. | Optional | 66.0 |
| `user​Context` | [User Context Input](./connect_requests_user_context_input.htm.md) | User context details. For example, account ID or contact ID. | Optional | 60.0 |
