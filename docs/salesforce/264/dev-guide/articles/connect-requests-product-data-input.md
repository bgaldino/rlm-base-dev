---
page_id: connect-requests-product-data-input
title: Product Data Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-product-data-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-api-requests
legacy_page_id: connect_requests_product_data_input.htm
fetched_at: 2026-11-25
---

# Product Data Input

Input representation of the product details such as the product ID and product selling model ID.

## JSON Example

```
  "productData": [
    {
      "productId": "01txx0000006ivJAAQ",
      "productSellingModelId": "0jPxx000000009hEAA"
    },
    {
      "productId": "01txx0000006ivLAAQ",
      "productSellingModelId": "0jPxx000000009iEAABB"
    }
  ]
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `productId` | String | ID of the product. | Required | 61.0 |
| `product​Selling​ModelId` | String | ID of the product selling model. | Optional | 61.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-product-data-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
