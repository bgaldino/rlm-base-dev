---
page_id: connect_resources_update_nodes.htm
title: Configurator Update Nodes (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_update_nodes.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Configurator Update Nodes (POST)

Update nodes in a product configuration.

Resource
:   ```
    /connect/cpq/configurator/actions/update-nodes
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/cpq/configurator/actions/update-nodes
    ```

Available version
:   60.0

HTTP methods
:   POST

Request body for POST
:   JSON example
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
            "updatedNodes": [
                {
                    "path": ["0Q0DE000000ISHJs81", "0QLDE000000IBXw4AO"],
                    "updatedAttributes": {
                        "Quantity": 5
                    }
                }
            ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `configurator​Options` | [Configurator Options Input](./connect_requests_configurator_options_input.htm.md "Input representation of the request to get the product configuration options that’s passed to the configurator.") | List of the configuration options to execute. | Optional | 60.0 |
        | `context​Id` | String | ID of the context object that’s being considered. | Required | 60.0 |
        | `qualification​Context` | [User Context Input](./connect_requests_configurator_user_context_input.htm.md "Input representation of the request to get the context details of a user, which are used for qualification rules.") | Context details that are used for the qualification rules. | Optional | 60.0 |
        | `updated​Nodes` | [Configurator Updated Node Input](./connect_requests_configurator_updated_node_input.htm.md "Input representation of the nodes to be updated in a product configuration.")[] | List of the nodes to be updated. | Required | 60.0 |

Response body for POST
:   [Configurator Update
    Nodes](./connect_responses_update_nodes_configurator_output.htm.md "Output representation of the configuration request details to update nodes.")
