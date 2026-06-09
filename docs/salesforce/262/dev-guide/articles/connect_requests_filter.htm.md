---
page_id: connect_requests_filter.htm
title: Filter Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_filter.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-06-09
---

# Filter Input

Input representation of the filter request.

JSON example
:   ```
    "filter": 
    {
    "criteria": [ {  
    "property": "name",   
    "operator": "eq",   
    "value": "iPhone"
    },
    {
    "criteriaType": "CustomWhereCondition",
    "value": "(effectiveenddate = null OR effectiveenddate >= 2024-06-25)"
    }
    ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `criteria` | [Criteria](./connect_requests_criteria.htm.md "Input representation of the filter criteria item request.")[] | Details of the filter criteria. | Required if the `filter` property is specified. | 60.0 |
