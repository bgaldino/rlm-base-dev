---
page_id: connect_requests_filter_input.htm
title: Filter Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_filter_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_requests.htm
fetched_at: 2026-06-09
---

# Filter Input

Input representation of the request to filter records.

JSON example
:   ```
    "filter":
     {"criteria":
     [ {
       "attributeType": "ProductStandard",
       "property": "name",
       "operator": "eq",
       "value": "iPhone"
     }]}
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `criteria` | [Filter Criteria Input](./connect_requests_filter_criteria_input.htm.md "Input representation of the criteria to filter records based on supported properties.")[] | Filter criteria to filter the records. | Optional | 60.0 |
