---
page_id: connect-resources-product-classification
title: Product Classification Details (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-product-classification.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-resources
legacy_page_id: connect_resources_product_classification.htm
fetched_at: 2026-11-25
---

# Product Classification Details (POST)

Retrieve the details for a list of product classification records.

This API fetches metadata, attributes, and attribute categories associated with product classifications across supported catalog systems.

**Resource**

```
/revenue/product-catalog-management/product-classifications/details
```

**Resource Example**

```
https://{yourInstance}.salesforce.com/services/data/v68.0/revenue/product-catalog-management/product-classifications/details
```

**Available Version:** 66.0

**HTTP Methods:** POST

**Request Body for POST**

**JSON Example**

```
{
  "productClassificationIds": [
    "01txx0000006iFMAAY",
    "01txx0000006iGxAAY"
  ],
  "catalogSystems": [
    "epc"
  ]
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `catalogSystems` | String[] | Name of the catalog system. Valid value is `epc`—Enterprise Product Catalog. | Optional | 66.0 |
| `product​ClassificationIds` | String[] | List of product classification IDs for which you want to retrieve product details. In the `epc` catalog system, these values are the `Product2` record IDs. | Required | 66.0 |

**Response Body for POST:** [Product Classification Details Collection](./connect-responses-product-classification-details-collection-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-product-classification.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
