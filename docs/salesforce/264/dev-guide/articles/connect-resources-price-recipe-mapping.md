---
page_id: connect-resources-price-recipe-mapping
title: Pricing Recipe Mapping (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-price-recipe-mapping.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-business-apis-rest-references
legacy_page_id: connect_resources_price_recipe_mapping.htm
fetched_at: 2026-11-25
---

# Pricing Recipe Mapping (POST)

Create a mapping between the pricing recipe and the Decision Tables. Post recipes with lookup tables or procedures.

## Resource

```
/connect/core-pricing/recipe/mapping
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/core-pricing/recipe/mapping
```

## Available Version

60.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
    "recipeId" : "12Gxx0000005J9MEAU",
    "pricingRecipeLookUpTableInputRepresentations": [
    {
      lookupId: “12Gxx0000005J9MEAU”, 
      pricingComponentType: “CustomDiscount”
  },
    {
      lookupId: “12Gxx0000005J9MEAU”, 
      pricingComponentType: “CustomDiscount”
  }
 ],
    "pricingRecipeProcedureInputRepresentation" : {
    "procedureId" : "9QLxx0000004C92GAE"
}
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `pricing​RecipeLookUp​Table​Input​Representations` | [Pricing Recipe LookUp Table Input](./connect-requests-pricing-recipe-look-up-table-input.md)[] | Input representation of the recipe mapping. | Required | 60.0 |
| `pricing​Recipe​Procedure​Input​Representation` | [Pricing Recipe Procedure Input](./connect-requests-pricing-recipe-procedure-input.md) | Input representation of the procedure that’s used in the pricing recipe. | Required | 60.0 |
| `recipeId` | String | ID of the pricing recipe. | Required | 60.0 |

## Response Body for POST

[Pricing Recipe Post](./connect-responses-pricing-recipe-post-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-price-recipe-mapping.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
