---
page_id: connect_requests_catalog_input.htm
title: Catalog Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_catalog_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-06-09
---

# Catalog Input

Input representation of the request to retrieve catalog records.

JSON example
:   This example shows how to retrieve catalogs that contain `apple` in the catalog name.
:   ```
    {
    "pageSize": 100,
    "offset": 0,
    "language": "french",
    "filter": {
    "criteria": [
    {
    "property": "name",
    "operator": "contains",
    "value": "apple"
    }
    ]
    }
    }
    ```
:   This example shows how to retrieve catalogs with `ServiceProcess` as the catalog type.
:   ```
    {
    "pageSize": 100,
    "offset": 0,
    "sort": {
      "orders": [
       {
       "property": "name",
       "direction": "desc"
       }
      ]
     },
    "filter": {
    "criteria": [
    {
    "property": "catalogType",
    "operator": "eq",
    "value": "ServiceProcess"
    }
    ]
    }
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Optional | 60.0 |
    | `filter` | [Filter](./connect_requests_criteria.htm.md "Input representation of the filter criteria item request.") | Criteria to filter the records. Filters are applicable to the fields of the ProductCatalog object. The supported operators are:   - `eq` - `in` - `contains`   The supported properties are `name` and `catalogType`. | Optional | 60.0 |
    | `language` | String | Custom language that you can specify to get translated data for the fields of an object that's enabled for translation. See [Translate Product and Product Category Data](https://help.salesforce.com/s/articleView?id=ind.product_catalog_translate_product2_and_productcategory_data.htm&language=en_US "HTML (New Window)"). | Optional | 64.0 |
    | `offset` | Integer | Number of records to skip. The default value is 0. | Optional | 60.0 |
    | `page​Size` | Integer | Number of records per page. Valid values are from 1 through 100. If unspecified, defaults to 100. | Optional | 60.0 |
    | `sort` | [Sort](./connect_requests_order.htm.md "Input representation of the sort order item request.") | Sort order of the catalog records. The supported operators are:   - `asc` - `desc` | Optional | 60.0 |
