---
page_id: connect_resources_get_category_by_ID.htm
title: Category By ID (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_category_by_ID.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-06-09
---

# Category By ID (GET)

Retrieve details of individual category records based
on a category ID.

Resource
:   ```
    /connect/pcm/categories/categoryId
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/pcm/categories/0ZGT100000000qqOAA
    ```

    ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/pcm/categories/0ZGT100000000qqOAA?language=spanish
    ```

Available version
:   60.0

Requires Chatter
:   No

HTTP methods
:   GET

Request parameters for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Optional | 60.0 |
    | `fields` | String[] | For internal use only. | Optional | 60.0 |
    | `language` | String | Custom language that you can specify to get translated data for the fields of an object that's enabled for translation. See [Translate Product and Product Category Data](https://help.salesforce.com/s/articleView?id=ind.product_catalog_translate_product2_and_productcategory_data.htm&language=en_US "HTML (New Window)"). | Optional | 64.0 |

Response body for GET
:   [Categories Output](./connect_responses_categories_output.htm.md "Output representation of the retrieved categories result.")
