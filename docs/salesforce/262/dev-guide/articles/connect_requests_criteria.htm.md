---
page_id: connect_requests_criteria.htm
title: Criteria Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_criteria.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-06-09
---

# Criteria Input

Input representation of the filter criteria item request.

JSON example
:   ```
    "criteria":
    [{
       "attributeType": "ProductStandard",
       "property": "name",
       "operator": "eq",
       "value": "iPhone"
    },
    {
       "criteriaType": "CustomWhereCondition",
       "value": "(effectiveenddate = null OR effectiveenddate >= 2024-06-25)"
    }
    ]
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `attributeType` | String | Search attribute type of the facet for a faceted search. Valid values are:   - `ProductStandard` - `ProductCustom` - `ProductDynamicAttribute` - `ProductAttributeStandard` - `ProductAttributeCustom`  This property is applicable if the **Use Indexed Data For Product Listing and Search** toggle from the Product Discovery Settings page from Setup is enabled. | Optional | 63.0 |
    | `criteriaType` | String | Type of criteria for the filter. Valid value is:  - `CustomWhereCondition` | Required | 60.0 |
    | `operator` | String | Operator used for the filter criteria. The supported operators are:   - `eq` - `in` - `contains`—This value isn’t   applicable if the **Use Indexed Data For Product Listing and   Search** toggle from the Product Discovery Settings page from   Setup is enabled. - `gt`—Specifies a greater than   criteria. Available from API version 63.0 and later for Number, Date, and   Datetime data types only. - `lt`—Specifies a less than   criteria. Available from API version 63.0 and later for Number, Date, and   Datetime data types only. - `gte`—Specifies a greater than   or equal to criteria. Available from API version 63.0 and later for   Number, Date, and Datetime data types only. - `lte`—Specifies a less than or   equal to criteria. Available from API version 63.0 and later for Number,   Date, and Datetime data types only. | Required | 60.0 |
    | `property` | String | Property name to use in the filter, which must be the same as the object field. | Required | 60.0 |
    | `value` | Object | Value for the filter criteria. | Required | 60.0 |
