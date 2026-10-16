---
page_id: connect_responses_update_favorite_output.htm
title: Configuration Update
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_update_favorite_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_responses.htm
fetched_at: 2026-09-29
---

# Configuration Update

Output representation of the details of the updated configuration.

    

## JSON Example

      
      

This example shows a sample when the update operation is successful.

      

```
{
  "errors": [],
  "success": true
}
```

      

This example shows a sample when the update operation has errors.

      

```
{
  "errors": [
    {
      "code": "INTERNAL_SERVER_ERROR",
      "message": "INVALID_REFERENCEOBJECTID"
    }
  ],
  "success": false
}
```

    

    
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Error Response](./connect_responses_configuration_list_error_response.htm.md) | List of errors that contains a message and an error code. | Small, 63.0 | 63.0 |
| `success` | Boolean | Indicates whether the update operation is successful (`true`) or not (`false`) | Small, 63.0 | 63.0 |
