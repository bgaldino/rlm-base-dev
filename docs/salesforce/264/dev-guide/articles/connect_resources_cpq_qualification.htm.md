---
page_id: connect_resources_cpq_qualification.htm
title: Qualification (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_cpq_qualification.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Qualification (POST)

Run the qualification procedure on a list of product IDs. This API
      is a composite API for Product Discovery.

    
      
        
          

**Resource**

          
: 
            

```
/connect/cpq/qualification
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/qualification
```

          

        
        
          

**Available version**

          
: 60.0

        
        
          

**HTTP methods**

          
: POST

        
        
          

**Request body for POST**

          
: 
            

**JSON example**

: 

```
{
  "productIds": [
    "01txx0000006i7PAAQ",
    "01txx0000006i7QAAQ",
    "01txx0000006i7IAAQ"
  ],
  "userContext": {
    "accountId": "001xx000003GZHgAAO"
  }
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `additional​ContextData` | [Context Data Input](./connect_requests_context_data_input.htm.md)[] | Additional nodes that are added to the custom or default context definition. The maximum number of supported nodes is 10. | Optional | 60.0 |
| `catalog​Id` | String | ID of the catalog. | Optional | 60.0 |
| `category​Id` | String | ID of the category. | Optional | 60.0 |
| `context​Definition` | String | API name of the custom context definition that’s sent for context creation. If this property isn’t specified, the default context definition is used. | Optional | 60.0 |
| `context​Mapping` | String | Default context mapping of the context definition. If a context mapping is specified, then the API checks whether the mapping belongs to the specified context definition to process the details for hydration. | Optional | 60.0 |
| `correlation​Id` | String | Unique identifier of the request. | Optional | 60.0 |
| `product​Ids` | String[] | List of product IDs for qualification check. | Required | 60.0 |
| `qualification​Procedure` | String | API name of the custom qualification procedure that’s sent for processing. If this property isn’t specified, the default qualification procedure is executed. | Optional | 60.0 |
| `user​Context` | [User Context Input](./connect_requests_user_context_input.htm.md) | User context details. For example, account ID or contact ID. | Optional | 60.0 |

          

        
        
          

**Response body for POST**

          
: [CPQ Base List](./connect_responses_cpq_base_list_output.htm.md)
