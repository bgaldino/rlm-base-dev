---
page_id: connect_requests_related_object_filters_input.htm
title: Related Object Filters Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_related_object_filters_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-06-09
---

# Related Object Filters Input

Input representation of the request to filter related objects.

JSON example
:   ```
    "relatedObjectFilters": 
    [{
       "criteria": [
        {
        "property": "IsCommercial",
        "operator": "eq",
        "value": true
        }
      ],
       "objectName": "ProductSpecificationRecType"
     }]
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `criteria` | [Criteria](./connect_requests_criteria.htm.md "Input representation of the filter criteria item request.")[] | Criteria to filter the related objects. | Required if the `relatedObjectFilters` property is specified. | 60.0 |
    | `objectName` | String | API name of the object that’s related to the main object. | Required if the `relatedObjectFilters` property is specified. | 60.0 |
