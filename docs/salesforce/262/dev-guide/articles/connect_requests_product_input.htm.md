---
page_id: connect_requests_product_input.htm
title: Product Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_product_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-06-09
---

# Product Input

Input representation of a product in the catalog.

JSON example
:   This example is a search request for products that contain `Bundle Product` in the product
    name.

    ```
    {
      "catalogIds": [
        "0ZST10000004D03OAE"
      ],
      "language": "spanish",
      "filter": {
        "criteria": [
          {
            "property": "name",
            "operator": "contains",
            "value": "Bundle Product"
          }
        ]
      },
      "relatedObjectFilters": [
        {
          "objectName": "ProductSpecificationRecType",
          "criteria": [
            {
              "property": "IsCommercial",
              "operator": "eq",
              "value": false
            }
          ],
          "additionalFields": {
            "Product2": {
              "fields": [
                "code__c"
              ]
            }
          }
        }
      ]
    }
    ```
:   This example is a search request for products that contain the specified search term
    in the product name and are part of a
    catalog.

    ```
      {
      "catalogIds": [
        "0ZSDU0000002Og54AE"
      ],
      "searchTerm": "Slack"
    }
    ```

Query parameters
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `product​Classification​Id` | String | ID of the product classification template that contains a collection of dynamic attributes and can be reused to create multiple products. Products that are based on a product classification inherit all the attributes of the product classification.  Specify either the product classification ID, list of category IDs, or list of catalog IDs to retrieve products. | Optional | 60.0 |

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `additional​Fields` | Map<String, [Additional Fields Input](./connect_requests_product_catalog_additional_fields_input.htm.md "Input representation of the additional standard or custom fields to be included in the response.")> | Map of the object and the list of standard and custom fields to be queried along with the standard response.  The supported object is Product2. | Optional | 61.0 |
    | `catalog​Ids` | List<String> | List of comma-separated catalog IDs. The API returns the list of product records that are associated with the specified catalog IDs.  Specify either the product classification ID, list of category IDs, or list of catalog IDs to retrieve products. | Optional | 60.0 |
    | `category​Ids` | List<String> | List of comma-separated category IDs. The API returns the list of product records that are associated with the specified category IDs. If unspecified, then returns all products that are added to at least one category.  Specify either the product classification ID, list of category IDs, or list of catalog IDs to retrieve products. | Optional | 60.0 |
    | `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Optional | 60.0 |
    | `filter` | [Criteria Input](./connect_requests_criteria.htm.md "Input representation of the filter criteria item request.") | Criteria to filter the records. Filters are applicable to the fields of Product2 object. The supported operators are:   - `eq` - `in` - `contains`—This value isn’t   applicable if the **Use Indexed Data For Product Listing and   Search** toggle from the Product Discovery Settings page from   Setup is enabled. - `gt`—Specifies a greater than   criteria. Available from API version 63.0 and later for Number, Date, and   Datetime data types only. - `lt`—Specifies a less than   criteria. Available from API version 63.0 and later for Number, Date, and   Datetime data types only. - `gte`—Specifies a greater than   or equal to criteria. Available from API version 63.0 and later for   Number, Date, and Datetime data types only. - `lte`—Specifies a less than or   equal to criteria. Available from API version 63.0 and later for Number,   Date, and Datetime data types only.   If multiple criteria are specified, then the criteria are combined by using the `and` operator.  The supported properties are `name`, `description`, and `isActive`. If the **Use Indexed Data For Product Listing and Search** toggle from the Product Discovery Settings page from Setup is enabled, then the supported property is `name` only. | Optional | 60.0 |
    | `language` | String | Custom language that you can specify to get translated data for the fields of an object that's enabled for translation. See [Translate Product and Product Category Data](https://help.salesforce.com/s/articleView?id=ind.product_catalog_translate_product2_and_productcategory_data.htm&language=en_US "HTML (New Window)"). | Optional | 64.0 |
    | `offset` | Integer | Number of records to skip. The default value is 0. | Optional | 60.0 |
    | `pageSize` | Integer | Specifies the number of records per page. Valid values are from 1 through 200. If the value is unspecified, it defaults to 100. | Optional | 60.0 |
    | `related​Object​Filters` | [Related Object Filter](./connect_requests_related_object_filters_input.htm.md "Input representation of the request to filter related objects.")[] | Criteria for the related objects to filter the records. The supported operator is `eq`. The supported object is `ProductSpecificationRecType`. The supported values are `true` and `false`. The supported property is `IsCommercial`. | Optional | 60.0 |
    | `searchTerm` | String | String used to get products with the product name containing the search term. See [Search Considerations When Using Indexed Data](https://help.salesforce.com/s/articleView?id=ind.product_catalog_search_considerations.htm&type=5&language=en_US "HTML (New Window)"). | Optional | 62.0 |
    | `sort` | [Sort](./connect_requests_order.htm.md "Input representation of the sort order item request.") | Sort order for the products.  If the **Use Indexed Data For Product Listing and Search** toggle from the Product Discovery Settings page from Setup is enabled, then you can sort products by using name only. | Optional | 60.0 |
