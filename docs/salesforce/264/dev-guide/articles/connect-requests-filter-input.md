---
page_id: connect-requests-filter-input
title: Filter Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-filter-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-api-requests
legacy_page_id: connect_requests_filter_input.htm
fetched_at: 2026-11-25
---

# Filter Input

Input representation of the request to filter records.

## JSON Example

```
"filter":
 {"criteria":
 [ {
   "attributeType": "ProductStandard",
   "property": "name",
   "operator": "eq",
   "value": "iPhone"
 }]}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `criteria` | [Filter Criteria Input](./connect-requests-filter-criteria-input.md)[] | Filter criteria to filter the records. | Optional | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-filter-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
