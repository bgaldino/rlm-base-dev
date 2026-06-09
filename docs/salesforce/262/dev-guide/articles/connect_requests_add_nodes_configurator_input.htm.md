---
page_id: connect_requests_add_nodes_configurator_input.htm
title: Configurator Add Nodes Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_add_nodes_configurator_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Configurator Add Nodes Input

Input representation of the request to add nodes within a root node.

JSON example
:   ```
    {
      "configuratorOptions": {
        "executePricing": true,
        "returnProductCatalogData": true,
        "qualifyAllProductsInTransaction": true,
        "validateProductCatalog": true,
        "validateAmendRenewCancel": true,
        "executeConfigurationRules": true,
        "addDefaultConfiguration": true
      },
      "qualificationContext": {
        "accountId": "001xx0000000001AAA",
        "contactId": "003xx00000000D7AAI"
      },
      "contextId": "008d27d7-e004-4906-a949-ee7d7c323c77",
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

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `added​Nodes` | [Configurator Added Node Input](./connect_requests_configurator_added_node_input.htm.md "Input representation of the nodes to be added to a product configuration.")[] | List of the nodes to be added. | Required | 60.0 |
    | `configurator​Options` | [Configurator Options Input](./connect_requests_configurator_options_input.htm.md "Input representation of the request to get the product configuration options that’s passed to the configurator.") | List of the configuration options to execute. | Optional | 60.0 |
    | `context​Id` | String | ID of the context object that’s being considered. | Required | 60.0 |
    | `qualification​Context` | [User Context Input](./connect_requests_configurator_user_context_input.htm.md "Input representation of the request to get the context details of a user, which are used for qualification rules.") | Context details that are used for the qualification rules. | Optional | 60.0 |
