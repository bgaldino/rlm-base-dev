---
page_id: connect_requests_pricing_recipe_input.htm
title: Pricing Recipe Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_pricing_recipe_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_requests.htm
fetched_at: 2026-11-23
---

# Pricing Recipe Input

Input representation to set up a pricing recipe page.

## JSON Example

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

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `pricing​RecipeLookUp​Table​Input​Representations` | [Pricing Recipe LookUp Table Input](./connect_requests_pricing_recipe_look_up_table_input.htm.md "Input representation of the lookup tables for the setup page recipe.")[] | Input representation of the recipe mapping. | Required | 60.0 |
| `pricing​Recipe​Procedure​Input​Representation` | [Pricing Recipe Procedure Input](./connect_requests_pricing_recipe_procedure_input.htm.md "Input representation of the procedure for the setup page recipe.") | Input representation of the procedure that’s used in the pricing recipe. | Required | 60.0 |
| `recipeId` | String | ID of the pricing recipe. | Required | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_pricing_recipe_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
