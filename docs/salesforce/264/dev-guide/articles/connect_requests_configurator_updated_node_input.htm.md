---
page_id: connect_requests_configurator_updated_node_input.htm
title: Configurator Updated Node Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_configurator_updated_node_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_requests.htm
fetched_at: 2026-09-29
---

# Configurator Updated Node Input

Input representation of the nodes to be updated in a product configuration.

    

## JSON Example

      
      

This example updates a field on an already-added sales transaction item. The path uses the persistent Salesforce record ID, not a `ref_*` reference. Only include the changed fields in `updatedAttributes`.

      

```
{
  "updatedNodes": [
    {
      "path": ["801xx0000000001AAA", "802xx0000000001AAA"],
      "updatedAttributes": {
        "businessObjectType": "OrderItem",
        "Quantity": 5
      }
    }
  ]
}
```

      

This example updates an attribute value on an already-added sales transaction item attribute. The path uses the persistent attribute record ID. Only include the changed fields in `updatedAttributes`. When a constraint model is active, include `AttributeName` and set it to the attribute’s developer name.

      

```
{
  "updatedNodes": [
    {
      "path": ["801xx0000000001AAA", "802xx0000000001AAA", "0AZxx0000000001AAA"],
      "updatedAttributes": {
        "businessObjectType": "OrderItemAttribute",
        "AttributeName": "Length",
        "AttributeValue": "10",
        "AttributePicklistValue": null
      }
    }
  ]
}
```

    

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `path` | String[] | Path to the node that’s being updated. | Required | 60.0 |
| `updated​Attributes` | Map<String, Object> | Details of the object that’s being updated. This property supports fields of objects from the Sales Transaction context definition, including custom objects and fields in your extended context definition. When you update an `OrderItemAttribute` or `QuoteLineItemAttribute` node and a constraint model is active, include `AttributeName` and set it to the product attribute’s developer name. For matching behavior and default fallback, see [Configurator API: Include the Attribute Developer Name When Creating or Updating Attributes](./cml_best_practice_attribute_name.htm.md). | Required | 60.0 |
