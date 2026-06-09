---
page_id: connect_requests_delete_nodes_configurator_input.htm
title: Configurator Delete Nodes Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_delete_nodes_configurator_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Configurator Delete Nodes Input

Input representation of the request to delete nodes from a product
configuration.

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
        "deletedNodes": [
            {
                "path": ["0Q0DE000000ISHJs81", "0QLDE000000IBXw4AO"]
            }
        ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `configurator​Options` | [Configurator Options Input](./connect_requests_configurator_options_input.htm.md "Input representation of the request to get the product configuration options that’s passed to the configurator.") | List of the configuration options to execute. | Optional | 60.0 |
    | `context​Id` | String | ID of the context object that’s being considered. | Required | 60.0 |
    | `deleted​Nodes` | [Configurator Deleted Node Input](./connect_requests_configurator_deleted_node_input.htm.md "Input representation of the nodes to be deleted from a product configuration.")[] | List of the nodes to be deleted. | Required | 60.0 |
    | `qualification​Context` | [User Context Input](./connect_requests_configurator_user_context_input.htm.md "Input representation of the request to get the context details of a user, which are used for qualification rules.") | Context details that are used for the qualification rules. | Optional | 60.0 |
