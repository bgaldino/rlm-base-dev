---
page_id: connect_responses_configurator_product_recommendation_output.htm
title: Configurator Product Recommendations
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_configurator_product_recommendation_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Configurator Product Recommendations

Output representation of the details of the product recommendations.

## JSON Example

```
{
  "productRecommendations": [
    {
      "referenceId": "CORE_BUNDLE_001",
      "productIds": [
        "01t000000001234",
        "01t000000005678"
      ]
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `productIds` | String[] | List of recommended product IDs. | Small, 65.0 | 65.0 |
| `referenceId` | String | Reference ID for the recommendation. | Small, 65.0 | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_configurator_product_recommendation_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
