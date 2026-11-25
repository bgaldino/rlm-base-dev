---
page_id: connect-responses-product-classification-output
title: Product Classification
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-classification-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_product_classification_output.htm
fetched_at: 2026-11-25
---

# Product Classification

Output representation of the product classification details.

## JSON Example

```
{
  "productClassification": {
    "id": "11BT10000004C9SMAU",
    "name": "class",
    "code": "code",
    "parentProductClassificationId": "11BDU0000004JXq2AM",
    "status": "Active"
  }
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | Code of the product classification record. | Small, 61.0 | 61.0 |
| `id` | String | ID of the product classification record. | Small, 60.0 | 60.0 |
| `name` | String | Name of the product classification record. If data translation is set up and specified in the org, the translated description is available. | Small, 61.0 | 61.0 |
| `parentProduct​Classification​Id` | String | ID of the parent product classification. | Small, 65.0 | 65.0 |
| `status` | String | Status of the product classification record. | Small, 61.0 | 61.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-classification-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
