---
page_id: connect_resources_get_product_by_ID.htm
title: Product Details (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_product_by_ID.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-06-09
---

# Product Details (GET)

Retrieve details of individual product records or a
bundle based on a product ID.

Resource
:   ```
    /connect/pcm/products/productId
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/pcm/products/01tT1000000F0afIAC
    ```

    ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/pcm/products/01tT1000000F0afIAC?language=spanish
    ```

    ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/pcm/products/01tT1000000F0afIAC/catalogSystems=epc
    ```

Available version
:   60.0

Requires Chatter
:   No

HTTP methods
:   GET
:   ![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

    #### Note

    You must invoke this API request by using GET method only. If the request is invoked by using
    POST method, the request is considered as a [Products List](./connect_resources_get_products.htm.md "Retrieve products. You can also search, filter, or sort the products.") API request.

Request parameters for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `catalogSystems` | String[] | Name of the catalog system. Valid values are:  - `epc`—Enterprise Product   Catalog - `pcm`—Product Catalog   Management  Although this parameter accepts a list, you can pass only one value. If you don’t specify a value, the default behavior is to fetch data from the `pcm` catalog. | Optional | 66.0 |
    | `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Optional | 60.0 |
    | `fields` | String[] | For internal use only. | Optional | 60.0 |
    | `language` | String | Custom language that you can specify to get translated data for the fields of an object that's enabled for translation. See [Translate Product and Product Category Data](https://help.salesforce.com/s/articleView?id=ind.product_catalog_translate_product2_and_productcategory_data.htm&language=en_US "HTML (New Window)"). | Optional | 64.0 |

Response body for GET
:   [Products](./connect_responses_products_output.htm.md "Output representation of the list of retrieved products.")
