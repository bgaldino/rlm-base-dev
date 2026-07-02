---
page_id: connect_requests_runtime_catalog_snapshot_input.htm
title: Run-time Catalog Snapshot Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_runtime_catalog_snapshot_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-06-09
---

# Run-time Catalog Snapshot Input

Input representation of the details of a run-time catalog snapshot for
deployment.

JSON example
:   ```
      "snapshot": {
        "activationType": "IMMEDIATE",
        "activationDate": "2024-05-06T05:12:59.000Z",
        "id": "1Avxx0000005DFe1AM"
      }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `activationDate` | String | Activation date of the snapshot. | Optional | 62.0 |
    | `activationType` | String | Activation type of the snapshot. Valid value is:  - `IMMEDIATE`—Snapshot is   activated immediately after a successful build. | Required | 62.0 |
    | `id` | String | ID of the snapshot. | Required | 62.0 |
