---
page_id: connect_requests_configurator_added_node_input.htm
title: Configurator Added Node Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_configurator_added_node_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_requests.htm
fetched_at: 2026-09-29
---

# Configurator Added Node Input

Input representation of the nodes to be added to a product configuration.

    

## JSON Example

      
      

```
{
  "addedNodes": [
    {
      "path": [
        "0Q0xx0000004EvcCAE",
        "ref_d3a3f8d2_e031_4517_ae28_69ce16cb6589"
      ],
      "addedObject": {
        "id": "ref_d3a3f8d2_e031_4517_ae28_69ce16cb6589",
        "SalesTransactionItemSource": "ref_d3a3f8d2_e031_4517_ae28_69ce16cb6589",
        "SalesTransactionItemParent": "0Q0xx0000004EvcCAE",
        "PricebookEntry": "01uxx00000090VuAAI",
        "ProductSellingModel": "0jPxx00000001KHEAY",
        "UnitPrice": 15.26,
        "Quantity": 1,
        "Product": "01txx0000006lfHAAQ",
        "businessObjectType": "QuoteLineItem"
      }
    },
    {
      "path": [
        "0Q0xx0000004EvcCAE",
        "ref_d3a3f8d2_e031_4517_ae28_69ce16cb6589",
        "ref_d85b036d_d305_4bb6_aba8_a1dff645a664"
      ],
      "addedObject": {
        "id": "ref_d85b036d_d305_4bb6_aba8_a1dff645a664",
        "MainItem": "0QLxx0000004QdRGAU",
        "AssociatedItem": "ref_d3a3f8d2_e031_4517_ae28_69ce16cb6589",
        "ProductRelatedComponent": "0dSxx00000001p6EAA",
        "ProductRelationshipType": null,
        "AssociatedItemPricing": "NotIncludedInBundlePrice",
        "AssociatedQuantScaleMethod": "Proportional",
        "businessObjectType": "QuoteLineRelationship"
      }
    }
  ]
}
```

      

This example shows a sample request for orders.

      

```
{
  "addedNodes": [
    {
      "path": [
        "0Q0xx0000004EvcCAE",
        "ref_d3a3f8d2_e031_4517_ae28_69ce16cb6589"
      ],
      "addedObject": {
        "id": "ref_d3a3f8d2_e031_4517_ae28_69ce16cb6589",
        "SalesTransactionItemSource": "ref_d3a3f8d2_e031_4517_ae28_69ce16cb6589",
        "SalesTransactionItemParent": "0Q0xx0000004EvcCAE",
        "PricebookEntry": "01uxx00000090VuAAI",
        "ProductSellingModel": "0jPxx00000001KHEAY",
        "UnitPrice": 15.26,
        "Quantity": 1,
        "Product": "01txx0000006lfHAAQ",
        "businessObjectType": "OrderItem"
      }
    },
    {
      "path": [
        "0Q0xx0000004EvcCAE",
        "ref_d3a3f8d2_e031_4517_ae28_69ce16cb6589",
        "ref_d85b036d_d305_4bb6_aba8_a1dff645a664"
      ],
      "addedObject": {
        "id": "ref_d85b036d_d305_4bb6_aba8_a1dff645a664",
        "MainItem": "0QLxx0000004QdRGAU",
        "AssociatedItem": "ref_d3a3f8d2_e031_4517_ae28_69ce16cb6589",
        "ProductRelatedComponent": "0dSxx00000001p6EAA",
        "ProductRelationshipType": null,
        "AssociatedItemPricing": "NotIncludedInBundlePrice",
        "AssociatedQuantScaleMethod": "Proportional",
        "businessObjectType": "OrderItemRelationship"
      }
    }
  ]
}
```

      

This example shows a single-call request that adds a parent bundle, a child product, a relationship, and an attribute in one payload. Use this pattern to minimize API round-trips when building cart flows. When a constraint model is active, include `AttributeName` and set it to the attribute’s developer name.

      

```
{
  "addedNodes": [
    {
      "path": [
        "801xx0000000001AAA",
        "ref_PrimLine"
      ],
      "addedObject": {
        "id": "ref_PrimLine",
        "SalesTransactionItemSource": "ref_PrimLine",
        "SalesTransactionItemParent": "801xx0000000001AAA",
        "PricebookEntry": "01uxx00000090VuAAI",
        "ProductSellingModel": "0jPxx00000001KHEAY",
        "UnitPrice": 100.0,
        "Quantity": 1,
        "Product": "01txx0000006lfHAAQ",
        "businessObjectType": "OrderItem"
      }
    },
    {
      "path": [
        "801xx0000000001AAA",
        "ref_ChildItem"
      ],
      "addedObject": {
        "id": "ref_ChildItem",
        "SalesTransactionItemSource": "ref_ChildItem",
        "SalesTransactionItemParent": "801xx0000000001AAA",
        "PricebookEntry": "01uxx00000090VuAAJ",
        "ProductSellingModel": "0jPxx00000001KHEAZ",
        "UnitPrice": 0.0,
        "Quantity": 1,
        "Product": "01txx0000006lfHAAR",
        "businessObjectType": "OrderItem"
      }
    },
    {
      "path": [
        "801xx0000000001AAA",
        "ref_ChildItem",
        "ref_Rel"
      ],
      "addedObject": {
        "id": "ref_Rel",
        "MainItem": "ref_PrimLine",
        "AssociatedItem": "ref_ChildItem",
        "ProductRelatedComponent": "0dSxx00000001p6EAA",
        "ProductRelationshipType": null,
        "AssociatedItemPricing": "IncludedInBundlePrice",
        "businessObjectType": "OrderItemRelationship"
      }
    },
    {
      "path": [
        "801xx0000000001AAA",
        "ref_ChildItem",
        "ref_LengthAttr"
      ],
      "addedObject": {
        "id": "ref_LengthAttr",
        "businessObjectType": "OrderItemAttribute",
        "AttributeName": "Length",
        "SalesTransactionItemAttrParent": "ref_ChildItem",
        "ParentReference": "ref_ChildItem",
        "AttributeKey": "0tjxx0000000001AAA",
        "AttributeValue": "5",
        "AttributePicklistValue": null
      }
    }
  ]
}
```

      

**Note:** Ordering constraint: within a single `addedNodes` array, an attribute node's `SalesTransactionItemAttrParent` must reference a parent that either already exists on the transaction or appears earlier in the same array. Attribute nodes (`businessObjectType: "OrderItemAttribute"` or `"QuoteLineItemAttribute"`) are never placed inline on the parent's `addedObject`; each attribute requires its own entry in the `addedNodes` array.

      

**Note:** When `businessObjectType` is `OrderItemAttribute` or `QuoteLineItemAttribute` and a constraint model is active, `addedObject` must include `AttributeName`. Set `AttributeName` to the product attribute’s developer name so the constraint engine can match the CML variable. `AttributeKey` doesn’t replace `AttributeName`. For matching behavior and default fallback, see [Configurator API: Include the Attribute Developer Name When Creating or Updating Attributes](./cml_best_practice_attribute_name.htm.md).

    

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `added​Object` | Map<String, Object> | Details of the object that’s being added. This property supports fields of objects from the Sales Transaction context definition, including custom objects and fields in your extended context definition. When `businessObjectType` is `OrderItemAttribute` or `QuoteLineItemAttribute` and a constraint model is active, include `AttributeName` and set it to the product attribute’s developer name. `AttributeKey` doesn’t replace `AttributeName`. | Required | 60.0 |
| `path` | String[] | Path to the node that’s being added. The path includes the unique ID of the context node in the data structure. This ID must match the ID of the sales transaction item source such as a quote line or an order line item. Keep these considerations in mind when setting the `path` value. If the `businessObjectType` property value is `QuoteLineItem` or `OrderItem`, the path must contain 2 IDs. The first ID is the transaction ID (quote or order), and the second ID is the line item ID; If the `businessObjectType` property value is `QuoteLineItem` or `OrderItem`, the `addedObject` must contain `SalesTransactionItemSource` and `SalesTransactionItemParent`; If the `businessObjectType` property value is `QuoteLineRelationship` or `OrderItemRelationship`, the path must contain 3 IDs. The first ID is the transaction ID. The second ID is the associated line item ID. The third ID is the relationship node ID; or If the `businessObjectType` property value is `QuoteLineItemAttribute` or `OrderItemAttribute`, the path must contain 3 IDs. The first ID is the transaction ID. The second ID is the parent line item ID. The third ID is the attribute node ID. The `addedObject` must contain `SalesTransactionItemAttrParent` set to the parent line item ID. | Required | 60.0 |
