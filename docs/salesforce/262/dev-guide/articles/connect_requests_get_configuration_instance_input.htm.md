---
page_id: connect_requests_get_configuration_instance_input.htm
title: Configuration Get Instance Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_get_configuration_instance_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Configuration Get Instance Input

Input representation of the request to get a product configuration instance.

JSON example
:   ```
    {
    "contextId": "008d27d7-e004-4906-a949-ee7d7c323c77"
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `contextId` | String | Transaction context ID of the product configuration instance that’s to be fetched. | Required | 60.0 |
