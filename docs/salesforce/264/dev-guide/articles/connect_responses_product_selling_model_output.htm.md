---
page_id: connect_responses_product_selling_model_output.htm
title: Product Selling Model
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_selling_model_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-11-23
---

# Product Selling Model

Output representation of the definition of the product selling model.

## JSON Example

```
"productSellingModel": 
{
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
| `name` | String | Name of the record. | Small, 60.0 | 60.0 |
| `pricing​Term` | Integer | Duration of the selling model. | Small, 60.0 | 60.0 |
| `pricing​Term​Unit` | String | Units of the pricing term. | Small, 60.0 | 60.0 |
| `selling​Model​Type` | String | Different models of selling the product. Valid values are `OneTime`, `TermDefined`, or `Evergreen`. | Small, 60.0 | 60.0 |
| `status` | String | Status of the selling model. For example, whether the selling model is active and can be used in transactions. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_selling_model_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
