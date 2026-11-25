---
page_id: connect-resources-get-catalogs-by-id
title: Catalog By ID (GET)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-get-catalogs-by-id.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-resources
legacy_page_id: connect_resources_get_catalogs_by_ID.htm
fetched_at: 2026-11-25
---

# Catalog By ID (GET)

Retrieve details of catalog records based on a catalog ID.

**Resource**

```
/connect/pcm/catalogs/{catalogId}
```

**Resource Example**

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/pcm/catalogs/{0ZST100000000kUOAQ}
```

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/pcm/catalogs/{0ZST100000000kUOAQ}?language=spanish
```

**Available Version:** 60.0

**Requires Chatter:** No

**HTTP Methods:** GET

**Request Parameters for GET**

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Optional | 60.0 |
| `fields` | String[] | For internal use only. | Optional | 60.0 |
| `language` | String | Custom language that you can specify to get translated data for the fields of an object that’s enabled for translation. See [Translate Product and Product Category Data](https://help.salesforce.com/s/articleView?id=ind.product_catalog_translate_product2_and_productcategory_data.htm). | Optional | 64.0 |

**Response Body for GET:** [Catalogs Output](./connect-responses-catalogs-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-get-catalogs-by-id.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
