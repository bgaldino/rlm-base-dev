---
page_id: connect-responses-pricing-model-output
title: Pricing Model
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-pricing-model-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-api-responses
legacy_page_id: connect_responses_pricing_model_output.htm
fetched_at: 2026-11-25
---

# Pricing Model

Output representation of the details of the pricing model.

## JSON Example

```
{
  "pricingModel": {
    "id": "0jPSG000000Avcv2AC",
    "name": "One Time",
    "pricingModelType": "OneTime"
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `frequency` | String | Details about the frequency of recurrence of the pricing model. | Small, 67.0 | 67.0 |
| `id` | String | ID of the pricing model. | Small, 67.0 | 67.0 |
| `name` | String | Name of the pricing model. | Small, 67.0 | 67.0 |
| `occurrence` | Integer | Details about the number of occurrences of the pricing model. | Small, 67.0 | 67.0 |
| `pricingModelType` | String | Type of the pricing model. | Small, 67.0 | 67.0 |
| `unitOfMeasure` | String | Unit of measure for the pricing model. | Small, 67.0 | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-pricing-model-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
