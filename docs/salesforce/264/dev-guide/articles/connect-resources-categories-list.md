---
page_id: connect-resources-categories-list
title: Categories List (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-categories-list.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-api-resources
legacy_page_id: connect_resources_categories_list.htm
fetched_at: 2026-11-25
---

# Categories List (POST)

Get a list of categories and subcategories of a specified catalog. This API is a composite API for Product Discovery.

## Resource

```
/connect/cpq/categories
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/cpq/categories
```

## Available Version

60.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
  "correlationId": "9cbb9650-48c5-11ed-96d1-0afcf185843b",
  "catalogId": "0ZSxx000000009hGAA",
  "userContext": {
      "accountId": "001xx0000000001AAA",
      "contactId": "003xx00000000D7AAI"
    }
}
```

This example shows a sample request to get a list of categories with eligible promotions.

```
{
  "correlationId": "9cbb9650-48c5-11ed-96d1-0afcf185843b",
  "catalogId": "0ZSxx000000009hGAA",
  "userContext": {
    "accountId": "001xx0000000001AAA",
    "contactId": "003xx00000000D7AAI"
  },
  "usePromotions": true
}
```

## Response Body for POST

[CPQ Base List](./connect-responses-cpq-base-list-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-categories-list.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
