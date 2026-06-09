---
page_id: connect_requests_set_configuration_instance_input.htm
title: Configuration Set Instance Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_set_configuration_instance_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Configuration Set Instance Input

Input representation of the request to set a product configuration instance.

JSON example
:   ```
    {
      "configuratorOptions": {
        "addDefaultConfiguration": true,
        "executeConfigurationRules": true,
        "executePricing": false,
        "qualifyAllProductsInTransaction": false,
        "validateAmendRenewCancel": false,
        "validateProductCatalog": false
      },
      "contextMappingId": "11jEk000017YdyUIAS",
      "qualificationContext": {
        "accountId": "001DU000001nHUGYA2"
      },
      "transaction": "{\"Quote\":[{\"QuoteLineItem\":[{\"businessObjectType\":\"QuoteLineItem\",\"id\":\"qli_1\"},{\"businessObjectType\":\"QuoteLineItem\",\"id\":\"qli_2\"},{\"businessObjectType\":\"QuoteLineItem\",\"id\":\"qli_3\"},{\"businessObjectType\":\"QuoteLineItem\",\"id\":\"qli_4\"}],\"businessObjectType\":\"Quote\",\"id\":\"aJSdm0000003m3JGAQ\"}]}"
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `configurator​Options` | [Configurator Options Input](./connect_requests_configurator_options_input.htm.md "Input representation of the request to get the product configuration options that’s passed to the configurator.") | List of the configurator options to execute. | Optional | 60.0 |
    | `context​MappingId` | String | ID of the context mapping record. | Required | 60.0 |
    | `qualification​Context` | [User Context Input](./connect_requests_configurator_user_context_input.htm.md "Input representation of the request to get the context details of a user, which are used for qualification rules.") | Context details that are used for the qualification rules. | Optional | 60.0 |
    | `transaction` | String | Transaction JSON payload representing an object in an external system that’s used to create a session. | Required | 60.0 |
