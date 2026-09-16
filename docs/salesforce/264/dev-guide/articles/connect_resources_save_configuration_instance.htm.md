---
page_id: connect_resources_save_configuration_instance.htm
title: Configuration Save Instance (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_save_configuration_instance.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Configuration Save Instance (POST)

Save a configuration instance after a successful product
      configuration.

    

Use the Configuration Save Instance API to save the changes to the source after a
        successful configuration. For example, save changes to the quote line item of a product,
        which is the source used to load the configuration.

        
          

**Resource**

          
: 
            

```
/connect/cpq/configurator/actions/save-instance
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/configurator/actions/save-instance
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
"contextId": "008d27d7-e004-4906-a949-ee7d7c323c77"
}
```

**Properties**

: 

                    

                    

                    

                    

                    

                  

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextId` | String | Transaction context ID of the product configuration instance that’s to be saved. | Required | 60.0 |

          

        
        
          

**Response body for POST**

          
: [Configuration Save
              Instance](./connect_responses_save_configuration_instance_output.htm.md)
