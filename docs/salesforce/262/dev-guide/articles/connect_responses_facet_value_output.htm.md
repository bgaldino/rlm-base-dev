---
page_id: connect_responses_facet_value_output.htm
title: Facet Value
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_facet_value_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Facet Value

Output representation of the facet values found in the search result.

JSON example
:   ```
          "values": [
            {
              "displayName": "Simple",
              "nameOrId": "Simple",
              "productCount": 9
            }
          ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `display​Name` | String | Display name of the facet value. | Small, 63.0 | 63.0 |
| `nameOr​Id` | String | Facet value name or ID. Reserved for internal use. | Small, 63.0 | 63.0 |
| `product​Count` |  | Number of products in the search result that match the facet value. | Small, 63.0 | 63.0 |
