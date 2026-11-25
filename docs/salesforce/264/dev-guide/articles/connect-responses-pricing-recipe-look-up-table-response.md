---
page_id: connect-responses-pricing-recipe-look-up-table-response
title: Pricing Recipe LookUp Table Response
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-pricing-recipe-look-up-table-response.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-responses
legacy_page_id: connect_responses_pricing_recipe_look_up_table_response.htm
fetched_at: 2026-11-25
---

# Pricing Recipe LookUp Table Response

Output representation of a pricing recipe lookup table.

## JSON Example

```
      "decisionTables": [
        {
          "id": "0lDxx00000000T3EAI",
          "isInternal": true,
          "pricingComponentType": "ListPrice"
        },
        {
          "id": "0lDxx00000000T4EAI",
          "isInternal": true,
          "pricingComponentType": "VolumeDiscount"
        },
        {
          "id": "0lDxx00000000HlEAI",
          "isInternal": false,
          "pricingComponentType": "CustomDiscount"
        }
      ]
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the pricing recipe table mapping. | Small, 60.0 | 60.0 |
| `is​Internal` | Boolean | Indicates if the decision table is available (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `pricing​Component​Type` | String | Price component types such as, custom discount, volume discount, attribute-based discount, bundle-based discount, and list price. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-pricing-recipe-look-up-table-response.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
