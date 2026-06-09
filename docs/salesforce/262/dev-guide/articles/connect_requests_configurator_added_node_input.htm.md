---
page_id: connect_requests_configurator_added_node_input.htm
title: Configurator Added Node Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_configurator_added_node_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Configurator Added Node Input

Input representation of the nodes to be added to a product configuration.

JSON example
:   ```
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
:   This example shows a sample request for
    orders.

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

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `added​Object` | Map<String, Object> | Details of the object that’s being added. This property supports fields of objects from the Sales Transaction context definition, including custom objects and fields in your extended context definition. | Required | 60.0 |
    | `path` | String[] | Path to the node that’s being added. The path includes the unique ID of the context node in the data structure. This ID must match the ID of the sales transaction item source such as a quote line or an order line item.  Keep these considerations in mind when setting the `path` value.   - If the `businessObjectType` property value is   `QuoteLineItem`, the path must contain 2   IDs. The first ID is the quote ID, and the second   ID is the quote line item ID. - If the `businessObjectType` property value is   `QuoteLineItem`, the path must contain   `SalesTransactionItemSource` and `SalesTransactionItemParent`. - If the `businessObjectType` property value is   `QuoteLineItemRelationship`, the path must   contain 3 IDs. The first ID is the quote ID. The   second ID is the quote line item ID. The third ID   is the quote line item relationship ID. | Required | 60.0 |
