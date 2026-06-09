---
page_id: connect_requests_include_object_input.htm
title: Include Object Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_include_object_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-06-09
---

# Include Object Input

Input representation of the object to include in the response.

JSON example
:   ```
    "includeObjects": 
    [{
    "objectName": "ProductCategory"
    }]
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `objectName` | String | Name of the object to include in the response. The supported object is `ProductCategory`. | Required if the `options` property is specified. | 60.0 |
