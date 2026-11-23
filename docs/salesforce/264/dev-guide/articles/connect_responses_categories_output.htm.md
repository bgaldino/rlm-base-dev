---
page_id: connect_responses_categories_output.htm
title: Categories Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_categories_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-11-23
---

# Categories Output

Output representation of the retrieved categories result.

## JSON Example

```
{
  "categories": [
    {
      "catalogId": "0ZS1Q000000XbZAWA0",
      "code": "B2B Category",
      "description": "Products Category",
      "hasSubCategories": true,
      "id": "0ZG1Q000000XbVGWA0",
      "name": "Unified Computing",
      "numberOfProducts": 2,
      "parentCategoryId": "0ZGT100000000qlOAA",
      "sortOrder": 2,
      "subCategories": [],
      "isNavigational: false
    }
  ],
  "correlationId": "30230973-0a09-405e-b148-f085bb6dd66e",
  "status": {
    "code": "200",
    "errors": [],
    "message": "Successfully fetched the category records."
  }
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `categories` | [Category Output](./connect_responses_category_output.htm.md "Output representation of the category definition.")[] | List of the retrieved categories. | Small, 60.0 | 60.0 |
| `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Small, 60.0 | 60.0 |
| `status` | [Status](./connect_responses_status.htm.md "Output representation of the status of the request.") | Status of the request. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_categories_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
