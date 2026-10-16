---
page_id: connect_resources_get_valid_pricing_elements.htm
title: Pricing Recipe Valid Elements (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_valid_pricing_elements.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_business_apis_rest_references.htm
fetched_at: 2026-09-29
---

# Pricing Recipe Valid Elements (GET)

Get the list of valid pricing element type API names for a given Pricing Usage Sub Type.

    

## Resource

      
      

```
/connect/core-pricing/revenue/pricing-recipe/valid-elements
```

    

    

## Resource Example

      
      

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/revenue/pricing-recipe/valid-elements?pricingUsageSubType=RevenueCloud
```

    

    

## Available Version

      
      

68.0

    

    

## HTTP Methods

      
      

GET

    

    

## Request Parameters for GET

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

          

        
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `pricingUsageSubType` | String | Pricing usage subtype to retrieve the valid element types for. Must match an entry in the PricingUsageSubType picklist. For example, `RevenueCloud`, `Loyalty`, `LifeSciences`, and `Commercial`. | Required | 68.0 |

    

    

## Response Body for GET

      
      

[Pricing Recipe Valid Elements](./connect_responses_pricing_valid_elements_output.htm.md)
