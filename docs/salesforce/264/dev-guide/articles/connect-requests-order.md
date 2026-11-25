---
page_id: connect-requests-order
title: Order Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-order.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-requests
legacy_page_id: connect_requests_order.htm
fetched_at: 2026-11-25
---

# Order Input

Input representation of the sort order item request.

**JSON Example**

```
"sort":{
"orders":
[{
   "property": "name",
   "direction": "asc"
}]
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `direction` | String | Direction to sort the list items, such as in ascending order or descending order. | Required | 60.0 |
| `property` | String | Property to use for the sorting of the list items. | Required | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-order.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
