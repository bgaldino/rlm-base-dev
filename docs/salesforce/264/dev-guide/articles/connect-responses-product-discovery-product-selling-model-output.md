---
page_id: connect-responses-product-discovery-product-selling-model-output
title: Product Selling Model
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-discovery-product-selling-model-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-api-responses
legacy_page_id: connect_responses_product_discovery_product_selling_model_output.htm
fetched_at: 2026-11-25
---

# Product Selling Model

Product Selling Model Component output representation

## JSON Example

```
{
  "productSellingModel": {
    "doesAutoRenewByDefault": false,
    "id": "0jPSG000000Avcv2AC",
    "name": "One Time",
    "sellingModelType": "OneTime",
    "status": "Active"
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `doesAutoRenewByDefault` | Boolean | Indicates whether the product is automatically renewed by default (`true`) or not (`false`). | Small, 67.0 | 67.0 |
| `id` | String | ID of the product selling model. | Small, 67.0 | 67.0 |
| `name` | String | Name of the product selling model. | Small, 67.0 | 67.0 |
| `pricingTerm` | Integer | Pricing term of the product selling model. | Small, 67.0 | 67.0 |
| `pricingTermUnit` | String | Pricing term unit of the product selling model. | Small, 67.0 | 67.0 |
| `sellingModelType` | String | Selling model type associated with the product selling model. | Small, 67.0 | 67.0 |
| `status` | String | Status of the product selling model. | Small, 67.0 | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-discovery-product-selling-model-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
