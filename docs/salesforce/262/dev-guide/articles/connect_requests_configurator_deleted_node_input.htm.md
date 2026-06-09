---
page_id: connect_requests_configurator_deleted_node_input.htm
title: Configurator Deleted Node Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_configurator_deleted_node_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Configurator Deleted Node Input

Input representation of the nodes to be deleted from a product configuration.

JSON example
:   ```
        "deletedNodes": [
            {
                "path": ["0Q0DE000000ISHJs81", "0QLDE000000IBXw4AO"]
            }
        ]
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `path` | String[] | Path to the node that’s being deleted. | Required | 60.0 |
