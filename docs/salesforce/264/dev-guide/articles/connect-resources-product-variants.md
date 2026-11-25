---
page_id: connect-resources-product-variants
title: Product Variants (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-product-variants.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-resources
legacy_page_id: connect_resources_product_variants.htm
fetched_at: 2026-11-25
---

# Product Variants (POST)

Retrieve the variation product associated with one or more parent variant products.

A parent variant product is a non-purchasable product that groups related variations. Use this API to retrieve the mapping between parent variant product IDs and their associated variation product IDs.

**Resource**

```
/connect/pcm/products/variants
```

**Resource Example**

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/pcm/products/variants
```

**Available Version:** 67.0

**Requires Chatter:** No

**HTTP Methods:** POST

**Note:** POST methods typically create an item, but for this resource POST is used to retrieve information.

**Request Body for POST**

**JSON Example**

```
{
  "correlationId": "9b6bc520-3c82-4d6c-a458-47590370681a",
  "parentVariantsIds": [
    "01tT1000000F0afIAC",
    "01tT1000000F0agIAC"
  ]
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `correlation​Id` | String | Unique ID to track and associate related events or transactions. If unspecified, a Universally Unique Identifier (UUID) is generated. | Optional | 67.0 |
| `parent​Variants​Ids` | String[] | List of product IDs for parent variant products whose variations you want to retrieve. If any product ID is blank, invalid, or not found, the API skips that ID and processes the remaining valid IDs. The skipped IDs appear in the `inValidProductIds` response property. If a product ID is valid but isn’t a parent variant product, the API includes it in the `nonVariantParentIds` response property. | Required | 67.0 |

**Response Body for POST:** [Product Variants](./connect-responses-product-variants-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-product-variants.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
