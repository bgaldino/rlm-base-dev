---
page_id: connect_requests_order.htm
title: Order Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_order.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-06-09
---

# Order Input

Input representation of the sort order item request.

JSON example
:   ```
    "sort":{
    "orders":
    [{
       "property": "name",
       "direction": "asc"
    }]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `direction` | String | Direction to sort the list items, such as in ascending order or descending order. | Required | 60.0 |
    | `property` | String | Property to use for the sorting of the list items. | Required | 60.0 |
