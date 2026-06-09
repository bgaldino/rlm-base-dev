---
page_id: connect_requests_configurator_updated_node_input.htm
title: Configurator Updated Node Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_configurator_updated_node_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Configurator Updated Node Input

Input representation of the nodes to be updated in a product configuration.

JSON example
:   ```
        "updatedNodes": [
            {
                "path": ["0Q0DE000000ISHJs81", "0QLDE000000IBXw4AO"],
                "updatedAttributes": {
                    "Quantity": 5
                }
            }
        ]
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `path` | String[] | Path to the node that’s being updated. | Required | 60.0 |
    | `updated​Attributes` | Map<String, Object> | Details of the object that’s being updated. This property supports fields of objects from the Sales Transaction context definition, including custom objects and fields in your extended context definition. | Required | 60.0 |
