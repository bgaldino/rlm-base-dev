---
page_id: connect_resources_get_index_errors.htm
title: Snapshot Index Error (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_index_errors.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-06-09
---

# Snapshot Index Error (GET)

Get the count and details of the errors that occurred during the
indexing process.

Resource
:   ```
    /connect/pcm/index/error
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/pcm/index/error
    ```

Available version
:   63.0

HTTP methods
:   GET

Request parameters for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `indexId` | String | ID of the index. | Required | 63.0 |
    | `snapshot​IndexId` | String | ID of the snapshot index. | Required | 63.0 |

Response body for GET
:   [Snapshot Index
    Error](./connect_responses_snapshot_index_error_output.htm.md "Output representation of the error details related to a snapshot index.")
