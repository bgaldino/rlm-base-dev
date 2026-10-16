---
page_id: connect_requests_pricing_request.htm
title: Pricing Request Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_pricing_request.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_requests.htm
fetched_at: 2026-09-29
---

# Pricing Request Input

Input representation of a pricing request.

    

## JSON Example

      
      

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

    

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `configuration​Overrides` | [Configuration Override Input](./connect_requests_configuration_override_input.htm.md) | Parameters to override pricing configuration. | Optional | 60.0 |
| `procedure​Name` | String | Name of the pricing procedure. | Optional | 60.0 |
