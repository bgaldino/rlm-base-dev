---
page_id: connect-responses-pricing-recipe-response
title: Pricing Recipe Response
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-pricing-recipe-response.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-responses
legacy_page_id: connect_responses_pricing_recipe_response.htm
fetched_at: 2026-11-25
---

# Pricing Recipe Response

Output representation of the pricing recipe.

## JSON Example

```
{
  "recipes": [
    {
      "active": false,
      "createdBy": "autoproc@00dxx0000006gmjea2",
      "createdOn": "2023-07-15T13:12:38.000Z",
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
      ],
      "developerName": "NGPDefaultRecipe",
      "id": "12Gxx0000005Ka4EAE",
      "name": "NGPDefaultRecipe",
      "procedureCreatedBy": "",
      "procedureCreatedOn": "2023-09-19T11:39:18.983Z",
      "procedureId": "",
      "procedureName": ""
    }],
  "success": true
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `recipes` | [Pricing Recipe Output Representation](./connect-responses-pricing-recipe-output.md)[] | Representation of the pricing recipe. | Small, 60.0 | 60.0 |
| `success` | Boolean | Indicates if the request is successful (`true`) or not (`false`). | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-pricing-recipe-response.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
