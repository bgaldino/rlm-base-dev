---
page_id: connect_requests_filter_input.htm
title: Filter Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_filter_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_requests.htm
fetched_at: 2026-11-23
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
| `criteria` | [Filter Criteria Input](./connect_requests_filter_criteria_input.htm.md "Input representation of the criteria to filter records based on supported properties.")[] | Filter criteria to filter the records. | Optional | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_filter_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
