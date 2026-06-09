---
page_id: connect_requests_configurator_options_input.htm
title: Configurator Options Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_configurator_options_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Configurator Options Input

Input representation of the request to get the product configuration options that’s
passed to the configurator.

JSON example
:   ```
        "configuratorOptions": 
          {
            "addDefaultConfiguration": true,
            "executeConfigurationRules": true,
            "executePricing": true,
            "qualifyAllProductsInTransaction": true,
            "validateAmendRenewCancel": true,
            "validateProductCatalog": true
        }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `add​Default​Configuration` | Boolean | Indicates whether to add the default configurations (`true`) or not (`false`). | Optional | 60.0 |
    | `execute​Configuration​Rules` | Boolean | Indicates whether to execute the configuration rules (`true`) or not (`false`). | Optional | 60.0 |
    | `execute​Pricing` | Boolean | Indicates whether to execute pricing (`true`) or not (`false`). | Optional | 60.0 |
    | `explainability​Enabled` | Boolean | Indicates whether additional metadata about how the solver achieved the execution request solution must be collected and made available to the caller (`true`) or not (`false`).  If you set this property to `true`, you can get explainability action logs by using the [Action Logs API](https://developer.salesforce.com/docs/atlas.en-us.262.0.industries_reference.meta/industries_reference/connect_resources_get_create_action_logs.htm "HTML (New Window)"). See [Troubleshoot Product Configurations](https://help.salesforce.com/s/articleView?id=ind.revenue_product_configuration_logs.htm&language=en_US "HTML (New Window)") to set up configuration logs. | Optional | 66.0 |
    | `pricing​Procedure` | String | Name of the pricing procedure to use during the API calls to Salesforce Pricing Management. | Optional | 60.0 |
    | `qualifyAll​ProductsIn​Transaction` | Boolean | Indicates whether to run the qualification rules on all the products in the context (`true`) or not (`false`). | Optional | 60.0 |
    | `returnProduct​Catalog​Data` | Boolean | Indicates whether to return the product catalog data (`true`) or not (`false`).  Exclude this property or specify the property value as `false` if you’re using the API without the Product Configurator UI. | Optional | 60.0 |
    | `validateAmend​Renew​Cancel` | Boolean | Indicates whether to run the amend, renew, cancel-related validations (`true`) or not (`false`). | Optional | 60.0 |
    | `validate​Product​Catalog` | Boolean | Indicates whether to run the validations against the product catalog (`true`) or not (`false`). | Optional | 60.0 |
