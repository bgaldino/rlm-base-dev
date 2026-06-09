---
page_id: connect_resources_snapshot_get.htm
title: Snapshot Collection (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_snapshot_get.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-06-09
---

# Snapshot Collection (GET)

Retrieve the created snapshots and snapshot indexes.

Resource
:   ```
    /connect/pcm/index/snapshots
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/pcm/index/snapshots
    ```

Available version
:   62.0

HTTP methods
:   GET

Query Parameter for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `numberOf​IndexLogs` | Integer | Number of index logs to include in the response. Specify a number from 0 through 100. The default value is 25. | Optional | 63.0 |

Response body for GET
:   [Snapshot
    Collection](./connect_responses_snapshot_collection_output.htm.md "Output representation of the retrieved snapshot collection.")
