---
page_id: connect-responses-product-configuration-rules-output
title: Product Configuration Rules
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-configuration-rules-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-api-responses
legacy_page_id: connect_responses_product_configuration_rules_output.htm
fetched_at: 2026-11-25
---

# Product Configuration Rules

Output representation of the details of the product configuration rules.

## JSON Example

```
{
  "configurationRules": [
    {
      "details": [
        {
          "message": "recommend Mouse from monitor"
        }
      ],
      "type": "recommend"
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `details` | [Product Configuration Rule Details](./connect-responses-product-configuration-rule-details-output.md)[] | Details of the product configuration rule. | Small, 67.0 | 67.0 |
| `type` | String | Type of the product configuration rule. | Small, 67.0 | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-configuration-rules-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
