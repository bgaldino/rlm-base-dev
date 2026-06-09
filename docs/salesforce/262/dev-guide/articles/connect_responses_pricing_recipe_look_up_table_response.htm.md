---
page_id: connect_responses_pricing_recipe_look_up_table_response.htm
title: Pricing Recipe LookUp Table Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_pricing_recipe_look_up_table_response.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Pricing Recipe LookUp Table Response

Output representation of a pricing recipe lookup table.

JSON example
:   ```
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
