---
page_id: connect-requests-filter
title: Filter Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-filter.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-requests
legacy_page_id: connect_requests_filter.htm
fetched_at: 2026-11-25
---

# Filter Input

Input representation of the filter request.

**JSON Example**

```
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

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `criteria` | [Criteria](./connect-requests-criteria.md)[] | Details of the filter criteria. | Required if the `filter` property is specified. | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-filter.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
