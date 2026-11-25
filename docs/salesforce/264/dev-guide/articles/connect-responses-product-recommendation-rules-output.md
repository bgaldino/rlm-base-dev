---
page_id: connect-responses-product-recommendation-rules-output
title: Product Recommendation Rules
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-recommendation-rules-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: connect-responses-config-rule-output
legacy_page_id: connect_responses_product_recommendation_rules_output.htm
fetched_at: 2026-11-25
---

# Product Recommendation Rules

Output representation of the details of the product recommendation rules.

## JSON Example

```
{
  "productRecommendationRules": [
    {
      "message": "32GB RDIMM recommends 16GB RDIMM",
      "productIds": [
        "01tVW000003l7uaYAA"
      ],
      "recordType": "Type",
      "referenceId": "0Q0VW000000z8yN0AQ"
    },
    {
      "message": "32GB RDIMM recommends 64GB RDIMM",
      "productIds": [
        "01tVW000003l7v6YAA"
      ],
      "recordType": "Type",
      "referenceId": "0Q0VW000000z8yN0AQ"
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `message` | String | Message to display with the product recommendation. | Small, 67.0 | 67.0 |
| `productIds` | String[] | List of recommended Product IDs. | Small, 67.0 | 67.0 |
| `recordType` | String | Record type associated with the recommendation. | Small, 67.0 | 67.0 |
| `referenceId` | String | Reference ID of the product recommendation rule. | Small, 67.0 | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-recommendation-rules-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
