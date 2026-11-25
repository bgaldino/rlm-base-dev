---
page_id: connect-requests-pricing-recipe-clone-input
title: Pricing Recipe Clone Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-pricing-recipe-clone-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-requests
legacy_page_id: connect_requests_pricing_recipe_clone_input.htm
fetched_at: 2026-11-25
---

# Pricing Recipe Clone Input

Input representation to clone a pricing recipe.

## JSON Example

```
{
    "recordId" : "0ClxX0000004CxWACU",
    "newPricingRecipeApiName" : "Cloned_Recipe",
    "newPricingRecipeName" : "Cloned Recipe",
    "pricingUsageSubType" : "Loyalty"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `new​Pricing​Recipe​ApiName` | String | API name of the cloned pricing recipe. | Required | 68.0 |
| `new​Pricing​Recipe​Name` | String | Name for the cloned pricing recipe. | Required | 68.0 |
| `pricing​Usage​SubType` | String | Pricing usage subtype of the cloned pricing recipe. If unspecified, the value from the source pricing recipe is used. | Optional | 68.0 |
| `recordId` | String | ID of the source pricing recipe to clone. | Required | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-pricing-recipe-clone-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
