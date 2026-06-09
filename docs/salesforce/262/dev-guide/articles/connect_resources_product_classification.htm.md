---
page_id: connect_resources_product_classification.htm
title: Product Classification Details (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_product_classification.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-06-09
---

# Product Classification Details (POST)

Retrieve the details for a list of product classification
records.

This API fetches metadata, attributes, and attribute categories associated with product
classifications across supported catalog systems.

Resource
:   ```
    /revenue/product-catalog-management/product-classifications/details
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/revenue/product-catalog-management/product-classifications/details
    ```

Available version
:   66.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "productClassificationIds": [
            "01txx0000006iFMAAY",
            "01txx0000006iGxAAY"
          ],
          "catalogSystems": [
            "epc"
          ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `catalogSystems` | String[] | Name of the catalog system. Valid value is:  - `epc`—Enterprise Product   Catalog | Optional | 66.0 |
        | `product​ClassificationIds` | String[] | List of product classification IDs for which you want to retrieve product details. In the `epc` catalog system, these values are the `Product2` record IDs. | Required | 66.0 |

Response body for POST
:   [Product Classification Details
    Collection](./connect_responses_product_classification_details_collection_output.htm.md "Output representation that contains a collection of product classification details along with any processing errors.")
