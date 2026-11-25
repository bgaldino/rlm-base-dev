---
page_id: connect-requests-product-classification-list-input
title: Product Classification List Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-product-classification-list-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-requests
legacy_page_id: connect_requests_product_classification_list_input.htm
fetched_at: 2026-11-25
---

# Product Classification List Input

Input representation of the request to retrieve a list of product classification records.

**JSON Example**

```
{
  "catalogSystem": "pcm",
  "searchTerm": "Mobile",
  "filter": {
    "criteria": [
      {
        "property": "name",
        "operator": "contains",
        "value": "Mobile"
      }
    ]
  },
  "sort": {
    "orders": [
      {
        "property": "name",
        "direction": "asc"
      }
    ]
  },
  "pageSize": 25,
  "offset": 0
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `catalogSystem` | String | Name of the catalog system. Valid values are `pcm`—Product Catalog Management or `epc`—Enterprise Product Catalog. If unspecified, the default catalog system is `pcm`. | Optional | 67.0 |
| `filter` | [Criteria Input](./connect-requests-criteria.md) | Criteria to filter the product classification records. The supported property is `name`. The supported operators are `eq`, `in`, or `contains`. If multiple criteria are specified, they’re combined by using the `and` operator. Each criterion supports only the `property`, `operator`, and `value` fields. | Optional | 67.0 |
| `offset` | Integer | Number of records to skip. The default value is 0. | Optional | 67.0 |
| `pageSize` | Integer | Specifies the number of records per page. Valid values are 5, 10, 25, 50, and 100. If unspecified, the default value is 100. | Optional | 67.0 |
| `searchTerm` | String | String used to search for product classifications with the product classification name containing the search term. | Optional | 67.0 |
| `sort` | [Order Input](./connect-requests-order.md) | Sort order for the product classifications. If unspecified, the default sort order is by name in ascending order. | Optional | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-product-classification-list-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
