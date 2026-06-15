---
page_id: connect_responses_pricing_recipe_output.htm
title: Pricing Recipe
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_pricing_recipe_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Pricing Recipe

Output representation of the pricing recipe information table.

JSON example
:   ```
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
        }]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `active` | Boolean | Indicates whether the recipe is active (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `created​By` | String | Details on who created the recipe. | Small, 60.0 | 60.0 |
| `created​On` | String | Date when the recipe was created. | Small, 60.0 | 60.0 |
| `decision​Tables` | [Pricing Recipe LookUp Table Response](./connect_responses_pricing_recipe_look_up_table_response.htm.md "Output representation of a pricing recipe lookup table.") [] | Decision tables linked to the recipe. | Small, 60.0 | 60.0 |
| `developer​Name` | String | API name of the recipe. | Small, 60.0 | 60.0 |
| `id` | String | ID of the recipe. | Small, 60.0 | 60.0 |
| `name` | String | Name of the recipe. | Small, 60.0 | 60.0 |
| `procedure​CreatedBy` | String | Details on who created the procedure. | Small, 60.0 | 60.0 |
| `procedure​CreatedOn` | String | Date when the procedure was created. | Small, 60.0 | 60.0 |
| `procedure​Id` | String | ID of the procedure. | Small, 60.0 | 60.0 |
| `procedure​Name` | String | Name of the procedure. | Small, 60.0 | 60.0 |
