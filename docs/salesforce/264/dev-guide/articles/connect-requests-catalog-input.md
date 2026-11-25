---
page_id: connect-requests-catalog-input
title: Catalog Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-catalog-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-requests
legacy_page_id: connect_requests_catalog_input.htm
fetched_at: 2026-11-25
---

# Catalog Input

Input representation of the request to retrieve catalog records.

**JSON Example**

This example shows how to retrieve catalogs that contain `apple` in the catalog name.

```
{
"pageSize": 100,
"offset": 0,
"language": "french",
"filter": {
"criteria": [
{
"property": "name",
"operator": "contains",
"value": "apple"
}
]
}
}
```

This example shows how to retrieve catalogs with `ServiceProcess` as the catalog type.

```
{
"pageSize": 100,
"offset": 0,
"sort": {
  "orders": [
   {
   "property": "name",
   "direction": "desc"
   }
  ]
 },
"filter": {
"criteria": [
{
"property": "catalogType",
"operator": "eq",
"value": "ServiceProcess"
}
]
}
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Optional | 60.0 |
| `filter` | [Filter](./connect-requests-criteria.md) | Criteria to filter the records. Filters are applicable to the fields of the ProductCatalog object. The supported operators are `eq`, `in`, or `contains`. The supported properties are `name` and `catalogType`. | Optional | 60.0 |
| `language` | String | Custom language that you can specify to get translated data for the fields of an object that’s enabled for translation. See [Translate Product and Product Category Data](https://help.salesforce.com/s/articleView?id=ind.product_catalog_translate_product2_and_productcategory_data.htm). | Optional | 64.0 |
| `offset` | Integer | Number of records to skip. The default value is 0. | Optional | 60.0 |
| `page​Size` | Integer | Number of records per page. Valid values are from 1 through 100. If unspecified, defaults to 100. | Optional | 60.0 |
| `sort` | [Sort](./connect-requests-order.md) | Sort order of the catalog records. The supported operators are `asc` or `desc`. | Optional | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-catalog-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
