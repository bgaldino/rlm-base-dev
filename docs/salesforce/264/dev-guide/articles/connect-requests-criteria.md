---
page_id: connect-requests-criteria
title: Criteria Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-criteria.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-requests
legacy_page_id: connect_requests_criteria.htm
fetched_at: 2026-11-25
---

# Criteria Input

Input representation of the filter criteria item request.

**JSON Example**

```
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

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `attributeType` | String | Search attribute type of the facet for a faceted search. Valid values are `ProductStandard`, `ProductCustom`, `ProductDynamicAttribute`, `ProductAttributeStandard`, or `ProductAttributeCustom`. This property is applicable if the **Use Indexed Data For Product Listing and Search** toggle from the Product Discovery Settings page from Setup is enabled. | Optional | 63.0 |
| `criteriaType` | String | Type of criteria for the filter. Valid value is `CustomWhereCondition`. | Required | 60.0 |
| `operator` | String | Operator used for the filter criteria. | Required | 60.0 |
| `property` | String | Property name to use in the filter, which must be the same as the object field. | Required | 60.0 |
| `value` | Object | Value for the filter criteria. | Required | 60.0 |

The supported operators are:

- `eq`

- `in`

- `contains`—This value isn’t applicable if the **Use Indexed Data For Product Listing and Search** toggle from the Product Discovery Settings page from Setup is enabled.

- `gt`—Specifies a greater than criteria. Available from API version 63.0 and later for Number, Date, and Datetime data types only.

- `lt`—Specifies a less than criteria. Available from API version 63.0 and later for Number, Date, and Datetime data types only.

- `gte`—Specifies a greater than or equal to criteria. Available from API version 63.0 and later for Number, Date, and Datetime data types only.

- `lte`—Specifies a less than or equal to criteria. Available from API version 63.0 and later for Number, Date, and Datetime data types only.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-criteria.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
