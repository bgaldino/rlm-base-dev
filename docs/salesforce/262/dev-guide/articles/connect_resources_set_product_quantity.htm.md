---
page_id: connect_resources_set_product_quantity.htm
title: Product Set Quantity (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_set_product_quantity.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Product Set Quantity (POST)

Set the quantity of a product through the runtime
system.

Resource
:   ```
    /connect/cpq/configurator/actions/set-product-quantity
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/cpq/configurator/actions/set-product-quantity
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
            "quantity": 20,
            "transactionLinePath": "Quote.QuoteLineItem.Quantity"
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `configurator​Options` | [Configurator Options Input](./connect_requests_configurator_options_input.htm.md "Input representation of the request to get the product configuration options that’s passed to the configurator.") | List of the configuration options to execute. | Optional | 60.0 |
        | `context​Id` | String | ID of the context object that’s being considered. | Required | 60.0 |
        | `qualification​Context` | [User Context Input](./connect_requests_configurator_user_context_input.htm.md "Input representation of the request to get the context details of a user, which are used for qualification rules.") | Context details that are used for the qualification rules. | Optional | 60.0 |
        | `quantity` | Integer | Value of the product quantity. | Required | 60.0 |
        | `transaction​Line​Path` | String[] | Path to the line item where the update to the quantity is applied. For example, Quote.QuoteLineItem.Quantity. | Required | 60.0 |

Response body for POST
:   [Product Quantity Set
    Configurator](./connect_responses_set_product_quantity_configurator_output.htm.md "Output representation of the request details to set product quantity.")
