---
page_id: connect_requests_sort.htm
title: Sort Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_sort.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-06-09
---

# Sort Input

Input representation of the sort request.

JSON example
:   ```
    "sort":
    {
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
    | `orders` | [Order](./connect_requests_order.htm.md "Input representation of the sort order item request.")[] | Details of the sort order. | Required if the `sort` property is specified. | 60.0 |
