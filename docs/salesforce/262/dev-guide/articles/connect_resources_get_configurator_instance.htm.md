---
page_id: connect_resources_get_configurator_instance.htm
title: Configuration Get Instance (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_configurator_instance.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Configuration Get Instance (POST)

Fetch the JSON representation of a product configuration. Use the
response to display the details of the product configuration instance on the Salesforce user
interface, or save the product configuration instance to an external system.

Resource
:   ```
    /connect/cpq/configurator/actions/get-instance
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/cpq/configurator/actions/get-instance
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
        | `contextId` | String | Transaction context ID of the product configuration instance that’s to be fetched. | Required | 60.0 |

Response body for POST
:   [Configuration Get
    Instance](./connect_responses_get_configuration_instance_output.htm.md "Output representation of the request to retrieve the configuration instance.")
