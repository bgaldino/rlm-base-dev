---
page_id: connect_responses_pricing_recipe_clone_output.htm
title: Pricing Recipe Clone
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_pricing_recipe_clone_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-11-23
---

# Pricing Recipe Clone

Output representation of the payload for the pricing recipe clone operation.

## JSON Example

```
{
    "isSuccess" : true,
    "newPricingRecipeId" : "0ClxX0000004D1AACU",
    "newPricingRecipeName" : "Cloned Recipe"
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | [Pricing Recipe Clone Error](./connect_responses_pricing_recipe_clone_error.htm.md "Output representation of the error response for the Pricing Recipe Clone API.") | Details of the error encountered during the clone operation, if any. | Big, 68.0 | 68.0 |
| `isSuccess` | Boolean | Indicates whether the clone operation was successful (`true`) or not (`false`). | Big, 68.0 | 68.0 |
| `new​Pricing​RecipeId` | String | ID of the cloned pricing recipe. | Big, 68.0 | 68.0 |
| `new​Pricing​RecipeName` | String | Name of the cloned pricing recipe. | Big, 68.0 | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_pricing_recipe_clone_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
