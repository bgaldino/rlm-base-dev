---
page_id: connect-requests-product-variants-input
title: Product Variants Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-product-variants-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-requests
legacy_page_id: connect_requests_product_variants_input.htm
fetched_at: 2026-11-25
---

# Product Variants Input

Input representation of the request to retrieve the variation products associated with parent variant products.

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-product-variants-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
