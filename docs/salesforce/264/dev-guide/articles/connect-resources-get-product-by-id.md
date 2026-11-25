---
page_id: connect-resources-get-product-by-id
title: Product Details (GET)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-get-product-by-id.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-resources
legacy_page_id: connect_resources_get_product_by_ID.htm
fetched_at: 2026-11-25
---

# Product Details (GET)

Retrieve details of individual product records or a bundle based on a product ID.

**Resource**

```
/connect/pcm/products/{productId}
```

**Resource Example**

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/pcm/products/{01tT1000000F0afIAC}
```

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/pcm/products/{01tT1000000F0afIAC}?language=spanish
```

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/pcm/products/{01tT1000000F0afIAC}/catalogSystems=epc
```

**Available Version:** 60.0

**Requires Chatter:** No

**HTTP Methods:** GET

**Note:** You must invoke this API request by using GET method only. If the request is invoked by using POST method, the request is considered as a [Products List](./connect-resources-get-products.md) API request.

**Request Parameters for GET**

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `catalogSystems` | String[] | Name of the catalog system. Valid values are `epc`—Enterprise Product Catalog or `pcm`—Product Catalog Management. Although this parameter accepts a list, you can pass only one value. If you don’t specify a value, the default behavior is to fetch data from the `pcm` catalog. | Optional | 66.0 |
| `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Optional | 60.0 |
| `fields` | String[] | For internal use only. | Optional | 60.0 |
| `language` | String | Custom language that you can specify to get translated data for the fields of an object that’s enabled for translation. See [Translate Product and Product Category Data](https://help.salesforce.com/s/articleView?id=ind.product_catalog_translate_product2_and_productcategory_data.htm). | Optional | 64.0 |

**Response Body for GET:** [Products](./connect-responses-products-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-get-product-by-id.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
