---
page_id: connect_requests_load_configuration_instance_input.htm
title: Configuration Load Instance Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_load_configuration_instance_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Configuration Load Instance Input

Input representation of the request to load a product configuration
instance.

JSON example
:   ```
    {
        "configuratorOptions": 
          {
            "addDefaultConfiguration": true,
            "executeConfigurationRules": true,
            "executePricing": true,
            "qualifyAllProductsInTransaction": true,
            "validateAmendRenewCancel": true,
            "validateProductCatalog": true
        },
        "qualificationContext": {
            "accountId": "001DU000001nHUGYA2"
        },
        "transactionId": "0Q0DU0000000XoN0AU"
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `configurator​Options` | [Configurator Options Input](./connect_requests_configurator_options_input.htm.md "Input representation of the request to get the product configuration options that’s passed to the configurator.") | List of the configurator options to execute. | Optional | 60.0 |
    | `context​Mapping​Id` | String | ID of the context mapping record. | Optional | 60.0 |
    | `qualification​Context` | [User Context Input](./connect_requests_configurator_user_context_input.htm.md "Input representation of the request to get the context details of a user, which are used for qualification rules.") | Context details that are used for the qualification rules. | Optional | 60.0 |
    | `transaction​Id` | String | Transaction ID of the header entity that’s used to create a session. For example, a Quote or an Order. | Required | 60.0 |
