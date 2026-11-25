---
page_id: connect-responses-product-selling-model-option-output
title: Product Selling Model Option
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-selling-model-option-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_product_selling_model_option_output.htm
fetched_at: 2026-11-25
---

# Product Selling Model Option

Output representation of the definition of the product selling model option.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## JSON Example

```
"productSellingModelOptions": [
   {
    "id": "0iOT10000004CMrMAM",
    "isDefault": false,
    "productId": "01tT1000000F0YyIAK",
    "productSellingModel": {
    "id": "0jPT10000004CAfMAM",
    "name": "OneTimePSM",
    "pricingTerm": 1,
    "pricingTermUnit": "Months",
    "sellingModelType": "TermDefined",
    "status": "Active"
  }
}]
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the record. | Small, 60.0 | 60.0 |
| `isDefault` | Boolean | Indicates whether this model option is the default product selling model option (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `product​Id` | String | ID of the product. | Small, 60.0 | 60.0 |
| `product​Selling​Model` | [Product Selling Model](./connect-responses-product-selling-model-output.md) | Master-detail field to the product selling model. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-selling-model-option-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
