---
page_id: connect_requests_product_classification_details_input.htm
title: Product Classification Details Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_product_classification_details_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-06-09
---

# Product Classification Details Input

Input representation of the request to fetch details of product classification records,
including their attributes and attribute categories.

JSON example
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
