---
page_id: connect_responses_product_discovery_category_output.htm
title: Category Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_discovery_category_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_responses.htm
fetched_at: 2026-11-23
---

# Category Details

Output representation of the details of a category.

## JSON Example

```
{
  "categories": [
    {
      "catalogId": "0ZSSG000001875O4AQ",
      "childCategories": [],
      "customFields": {},
      "eligiblePromotions": [],
      "id": "0ZGSG000001DJtv4AG",
      "name": "Accessories",
      "qualificationContext": {
        "isQualified": true
      }
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `catalogId` | String | ID of the catalog the requested category belong to. | Small, 67.0 | 67.0 |
| `customFields` | Map<String, Object> | Details of the custom fields associated with a catalog. | Small, 67.0 | 67.0 |
| `description` | String | Description of the category. | Small, 67.0 | 67.0 |
| `eligiblePromotions` | [Promotion Output](./connect_responses_promotion_output.htm.md "Output representation of the details of applicable promotions.")[] | List of eligible promotions for the product. | Small, 67.0 | 67.0 |
| `hasSubCategories` | Boolean | Indicates whether the subcategories are available (`true`) or not (`false`). | Small, 67.0 | 67.0 |
| `id` | String | ID of the category. | Small, 67.0 | 67.0 |
| `isNavigational` | Boolean | Indicates whether the category node is navigational (`true`) or not (`false`). | Small, 67.0 | 67.0 |
| `name` | String | Name of the category. | Small, 67.0 | 67.0 |
| `parentCategoryId` | String | ID of the parent category. | Small, 67.0 | 67.0 |
| `qualificationContext` | [Qualification Context Output](./connect_responses_qualification_context_output.htm.md "Output representation of the details about the product qualification.")[] | Context details of a user, which are used for qualification rules. | Small, 67.0 | 67.0 |
| `sortOrder` | Integer | Display order of the product category relative to the siblings with the same parent category. | Small, 67.0 | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_discovery_category_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
