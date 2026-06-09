---
page_id: connect_requests_pricing_recipe_look_up_table_input.htm
title: Pricing Recipe LookUp Table Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_pricing_recipe_look_up_table_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_requests.htm
fetched_at: 2026-06-09
---

# Pricing Recipe LookUp Table Input

Input representation of the lookup tables for the setup page recipe.

JSON example
:   ```
        "pricingRecipeLookUpTableInputRepresentations": [
        {
          lookupId: “12Gxx0000005J9MEAU”, 
          pricingComponentType: “CustomDiscount”
      },
        {
          lookupId: “12Gxx0000005J9MEAU”, 
          pricingComponentType: “CustomDiscount”
      }
     ]
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `lookup​TableId` | String | ID of the decision table. | Optional | 60.0 |
    | `pricing​Component​Type` | String | Pricing component types such as volume discount, custom discount, attribute-based discount, and bundle-based discount. | Optional | 60.0 |
