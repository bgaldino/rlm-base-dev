---
page_id: connect_resources_price_context.htm
title: Price Context (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_price_context.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_business_apis_rest_references.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Price Context (POST)

Perform a pricing request by using the instance ID of a
      context.

    

If price waterfall is disabled from Salesforce Pricing Setup in your org, this API
        doesn't return the waterfall details. You can use the [Price Waterfall API](./connect_resources_pricing_waterfall_fetch.htm.md) to
        retrieve the waterfall details if price waterfall persistence is enabled in Salesforce
        Pricing Setup.

    
      
        
          

**Resource**

          
: 
            

```
/connect/core-pricing/price-contexts/contextid
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/price-contexts/0U3RM00000000SR0AY
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
    "configurationOverrides": {
       "skipWaterfall": true,
       "useSessionScopedContext": true,
       "persistContext": true,
       "taggedData": false
    }
    "procedureName": "ES1"
}

```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `configuration​Overrides` | [Configuration Override Input](./connect_requests_configuration_override_input.htm.md) | Parameters to override pricing configuration. | Optional | 60.0 |
| `procedure​Name` | String | Name of the pricing procedure. | Optional | 60.0 |

          

        
        
          

**Response body for POST**

          
: [Pricing Response](./connect_responses_pricing_response.htm.md)
