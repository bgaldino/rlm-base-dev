---
page_id: connect_resources_set_configurator_instance.htm
title: Configuration Set Instance (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_set_configurator_instance.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Configuration Set Instance (POST)

Set a product configuration instance. This API is used in scenarios
      where the configuration instance is available in a different database than Salesforce and the
      product catalog management data is in Salesforce.

    
      
        
          

**Resource**

          
: 
            

```
/connect/cpq/configurator/actions/set-instance
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/configurator/actions/set-instance
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
  "configuratorOptions": {
    "addDefaultConfiguration": true,
    "executeConfigurationRules": true,
    "executePricing": false,
    "qualifyAllProductsInTransaction": false,
    "validateAmendRenewCancel": false,
    "validateProductCatalog": false
  },
  "contextMappingId": "11jEk000017YdyUIAS",
  "qualificationContext": {
    "accountId": "001DU000001nHUGYA2"
  },
  "transaction": "{\"Quote\":[{\"QuoteLineItem\":[{\"businessObjectType\":\"QuoteLineItem\",\"id\":\"qli_1\"},{\"businessObjectType\":\"QuoteLineItem\",\"id\":\"qli_2\"},{\"businessObjectType\":\"QuoteLineItem\",\"id\":\"qli_3\"},{\"businessObjectType\":\"QuoteLineItem\",\"id\":\"qli_4\"}],\"businessObjectType\":\"Quote\",\"id\":\"aJSdm0000003m3JGAQ\"}]}"
}
```

          

**Properties**

: 

                    

                    

                    

                    

                    

                  

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `configurator​Options` | [Configurator Options Input](./connect_requests_configurator_options_input.htm.md) | List of the configurator options to execute. | Optional | 60.0 |
| `context​MappingId` | String | ID of the context mapping record. | Required | 60.0 |
| `qualification​Context` | [User Context Input](./connect_requests_configurator_user_context_input.htm.md) | Context details that are used for the qualification rules. | Optional | 60.0 |
| `transaction` | String | Transaction JSON payload representing an object in an external system that’s used to create a session. | Required | 60.0 |

          

        
        
          

**Response body for POST**

          
: [Configuration Set
              Instance](./connect_responses_set_configuration_instance_output.htm.md)
