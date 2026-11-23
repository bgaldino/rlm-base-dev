---
page_id: connect_requests_filter_criteria_input.htm
title: Filter Criteria Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_filter_criteria_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_requests.htm
fetched_at: 2026-11-23
---

# Filter Criteria Input

Input representation of the criteria to filter records based on supported properties.

## JSON Example

```
"criteria":
 [{
   "attributeType": "ProductStandard",
   "property": "name",
   "operator": "eq",
   "value": "iPhone"
 }]
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `attributeType` | String | Search attribute type of the facet for a faceted search. | Optional | 63.0 |
| `operator` | String | Operator used for the filter criteria. | Required | 60.0 |
| `property` | String | Property name to use in the filter, which must be the same as the object field. The supported property is `name`. | Required | 60.0 |
| `value` | Object | Value for the filter criteria. | Required | 60.0 |

Valid values are:

- `ProductStandard`
- `ProductCustom`
- `ProductDynamicAttribute`
- `ProductAttributeStandard`
- `ProductAttributeCustom`

The supported operators are:

- `eq`
- `in`
- `contains`
- `gt`—Specifies a greater than criteria. Available from API version 63.0 and later for Number, Date, and Datetime data types only.
- `lt`—Specifies a less than criteria. Available from API version 63.0 and later for Number, Date, and Datetime data types only.
- `gte`—Specifies a greater than or equal to criteria. Available from API version 63.0 and later for Number, Date, and Datetime data types only.
- `lte`—Specifies a less than or equal to criteria. Available from API version 63.0 and later for Number, Date, and Datetime data types only.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_filter_criteria_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
