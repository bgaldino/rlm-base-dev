---
page_id: connect_resources_categories_list.htm
title: Categories List (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_categories_list.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_resources.htm
fetched_at: 2026-06-09
---

# Categories List (POST)

Get a list of categories and subcategories of a specified catalog.
This API is a composite API for Product Discovery.

Resource
:   ```
    /connect/cpq/categories
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/cpq/categories
    ```

Available version
:   60.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "correlationId": "9cbb9650-48c5-11ed-96d1-0afcf185843b",
          "catalogId": "0ZSxx000000009hGAA",
          "userContext": {
              "accountId": "001xx0000000001AAA",
              "contactId": "003xx00000000D7AAI"
            }
        }
        ```

        This example shows a sample request to get a list of categories with eligible
        promotions.

        ```
        {
          "correlationId": "9cbb9650-48c5-11ed-96d1-0afcf185843b",
          "catalogId": "0ZSxx000000009hGAA",
          "userContext": {
            "accountId": "001xx0000000001AAA",
            "contactId": "003xx00000000D7AAI"
          },
          "usePromotions": true
        }
        ```

Response body for POST
:   [CPQ Base List](./connect_responses_cpq_base_list_output.htm.md "Output representation of the list of catalogs, categories, or products based on the request.")
