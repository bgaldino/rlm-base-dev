---
page_id: connect_resources_product_classification_list.htm
title: Product Classification List (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_product_classification_list.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-06-09
---

# Product Classification List (POST)

Retrieve a list of product classification records. You can also
search, filter, or sort the product classifications.

This API retrieves a paginated list of product classification records from the Product
Catalog Management (PCM) or Enterprise Product Catalog (EPC) catalog system. You can search
for product classifications by name, apply filters, and sort the results.

Resource
:   ```
    /revenue/product-catalog-management/product-classifications/list
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/revenue/product-catalog-management/product-classifications/list
    ```

Available version
:   67.0

HTTP methods
:   POST

    ![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

    #### Note

    POST methods typically create an item, but for this resource POST is used to
    retrieve information.

Request body for POST
:   JSON example
    :   ```
        {
          "catalogSystem": "pcm",
          "searchTerm": "Mobile",
          "filter": {
            "criteria": [
              {
                "property": "name",
                "operator": "contains",
                "value": "Mobile"
              }
            ]
          },
          "sort": {
            "orders": [
              {
                "property": "name",
                "direction": "asc"
              }
            ]
          },
          "pageSize": 25,
          "offset": 0
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `catalogSystem` | String | Name of the catalog system. Valid values are:  - `pcm`—Product Catalog   Management - `epc`—Enterprise Product   Catalog  If unspecified, the default catalog system is `pcm`. | Optional | 67.0 |
        | `filter` | [Criteria Input](./connect_requests_criteria.htm.md "Input representation of the filter criteria item request.") | Criteria to filter the product classification records. The supported property is `name`. The supported operators are:   - `eq` - `in` - `contains`   If multiple criteria are specified, they're combined by using the `and` operator.  Each criterion supports only the `property`, `operator`, and `value` fields. | Optional | 67.0 |
        | `offset` | Integer | Number of records to skip. The default value is 0. | Optional | 67.0 |
        | `pageSize` | Integer | Specifies the number of records per page. Valid values are 5, 10, 25, 50, and 100. If unspecified, the default value is 100. | Optional | 67.0 |
        | `searchTerm` | String | String used to search for product classifications with the product classification name containing the search term. | Optional | 67.0 |
        | `sort` | [Order Input](./connect_requests_order.htm.md "Input representation of the sort order item request.") | Sort order for the product classifications.  If unspecified, the default sort order is by name in ascending order. | Optional | 67.0 |

Response body for POST
:   [Product Classification List
    Collection](./connect_responses_product_classification_list_collection_output.htm.md "Output representation that contains a collection of product classification records along with any processing errors.")
