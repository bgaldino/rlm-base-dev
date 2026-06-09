---
page_id: connect_resources_unit_of_measure_info.htm
title: Unit of Measure Info (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_unit_of_measure_info.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-06-09
---

# Unit of Measure Info (GET)

Get details about the unit of measure for a specific set of
records.

Resource
:   ```
    /connect/pcm/unit-of-measure/info
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/pcm/unit-of-measure/info
    ```

Available version
:   63.0

HTTP methods
:   GET

Query parameters for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `correlationId` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Optional | 63.0 |
    | `ids` | String | IDs of the unit of measure records. | Optional | 63.0 |

Response body for GET
:   [Bulk Unit Of Measure
    Info](./connect_responses_bulk_unit_of_measure_info_output.htm.md "Output representation of the details of the unit of measure records along with error details.")
