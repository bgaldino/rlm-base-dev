---
page_id: connect_resources_save_configuration_instance.htm
title: Configuration Save Instance (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_save_configuration_instance.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Configuration Save Instance (POST)

Save a configuration instance after a successful product
configuration.

Use the Configuration Save Instance API to save the changes to the source after a
successful configuration. For example, save changes to the quote line item of a product,
which is the source used to load the configuration.

Resource
:   ```
    /connect/cpq/configurator/actions/save-instance
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/cpq/configurator/actions/save-instance
    ```

Available version
:   60.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
        "contextId": "008d27d7-e004-4906-a949-ee7d7c323c77"
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `contextId` | String | Transaction context ID of the product configuration instance that’s to be saved. | Required | 60.0 |

Response body for POST
:   [Configuration Save
    Instance](./connect_responses_save_configuration_instance_output.htm.md "Output representation of the response that’s returned with a save configuration request.")
