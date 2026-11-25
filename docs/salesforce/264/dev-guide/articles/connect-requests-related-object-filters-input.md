---
page_id: connect-requests-related-object-filters-input
title: Related Object Filters Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-related-object-filters-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-requests
legacy_page_id: connect_requests_related_object_filters_input.htm
fetched_at: 2026-11-25
---

# Related Object Filters Input

Input representation of the request to filter related objects.

**JSON Example**

```
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

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `criteria` | [Criteria](./connect-requests-criteria.md)[] | Criteria to filter the related objects. | Required if the `relatedObjectFilters` property is specified. | 60.0 |
| `objectName` | String | API name of the object that’s related to the main object. | Required if the `relatedObjectFilters` property is specified. | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-related-object-filters-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
