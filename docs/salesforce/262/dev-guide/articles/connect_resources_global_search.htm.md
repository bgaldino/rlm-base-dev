---
page_id: connect_resources_global_search.htm
title: Global Search (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_global_search.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_resources.htm
fetched_at: 2026-06-09
---

# Global Search (POST)

Retrieves a list of products based on a search query or search term.
This API is a composite API for Product Discovery.

Resource
:   ```
    /connect/cpq/products/search
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/cpq/products/search
    ```

Available version
:   60.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   This example shows a sample request to search products by using a
        query.

        ```
        {
          "query": {
            "textQuery": {
              "searchPhrase": "firstproduct"
            }
          },
          "catalogId": "0ZSxx0000000001GAA",
          "categoryId": "0ZGT100000000qlOAA",
          "correlationId": "9cbb9650-48c5-11ed-96d1-0afcf185843b",
          "limit": 10,
          "cursor": "MTAwMDAwMDAwNg==",
          "orderBy": [
            "name:asc",
            "id:desc"
          ],
          "userContext": {
            "accountId": "001xx0000000001AAA",
            "contactId": "003xx00000000D7AAI"
          },
          "additionalFields": {
            "Product2": {
              "fields": [
                "CustomField1__c",
                "CustomField2__c",
                "StandardField1"
              ]
            }
          }
        }
        ```
    :   This example shows a sample request to search products by using the `searchTerm`
        property.

        ```
        {
          "searchTerm": "Laptop",
          "catalogId": "0ZSDU0000002Og64AE",
          "categoryId": "0ZGDU0000002P0A4AU",
          "correlationId": "d9d8f898-19f5-464a-ba2b-6a070783f6c4",
          "limit": 10,
          "cursor": "MTAwMDAwMDAwNw==",
          "orderBy": [
            "name:asc",
            "id:desc"
          ],
          "userContext": {
            "accountId": "001DU000001o2V0YAI"
          }
        }
        ```

        If a parent category ID is specified in the request body, then the API
        returns all products associated to all child categories.
    :   This example shows a sample request to search products with eligible promotions. To
        fetch eligible promotions, specify a value for the `query` or `searchTerm` property, and set
        the `usePromotions` property to `true`.

        ```
        {
          "query": {
            "textQuery": {
              "searchPhrase": "laptop"
            }
          },
          "catalogId": "0ZSxx0000000001GAA",
          "categoryId": "0ZGT100000000qlOAA",
          "correlationId": "9cbb9650-48c5-11ed-96d1-0afcf185843b",
          "limit": 10,
          "cursor": "MTAwMDAwMDAwNg==",
          "orderBy": [
            "name:asc",
            "id:desc"
          ],
          "userContext": {
            "accountId": "001xx0000000001AAA",
            "contactId": "003xx00000000D7AAI"
          },
          "additionalFields": {
            "Product2": {
              "fields": [
                "CustomField1__c",
                "CustomField2__c",
                "StandardField1"
              ]
            }
          },
          "usePromotions": true
        }
        ```
    :   This example shows a sample request to run visibility
        rules.

        ```
        {
          "enableQualification": true,
          "enablePricing": true,
          "includeCatalogDetails": true,
          "searchTerm": "128GB LRDIMM",
          "catalogId": "0ZSVW000000AhdC4AS",
          "limit": 12,
          "userContext": {
            "accountId": null
          },
          "priceBookId": "01sVW0000024PZlYAM",
          "currencyCode": "USD",
          "transactionId": "0Q0VW000001190f0AA",
          "filter": {
            "criteria": [
              {
                "property": "isActive",
                "operator": "eq",
                "value": true
              },
              {
                "property": "UsedFor",
                "operator": "eq",
                "value": ""
              }
            ]
          },
          "orderBy": [
            "name:asc"
          ],
          "executeConfigurationRules": true
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `additional​Context​Data` | [Context Data Input](./connect_requests_context_data_input.htm.md "Input representation of the context data.")[] | Additional nodes that are added to the custom or default context definition. The maximum number of supported nodes is 10. | Optional | 60.0 |
        | `additional​Fields` | Map<String, [Additional Fields Input](./connect_requests_additional_fields_input.htm.md "Input representation of the additional standard or custom fields to include in the response.")> | Additional standard or custom fields of the Product2 object to include in the response.  If the requested fields are invalid or access to fields isn’t available, then the API throws an error. | Optional | 61.0 |
        | `catalog​Id` | String | ID of the catalog. If the catalog ID is specified, then the API returns the list of offers from the catalog with the pricing details related to the catalog. | Optional | 60.0 |
        | `category​Id` | String | ID of the category. If the category ID isn’t specified, then the API returns the matching query offers from the catalog. | Optional | 60.0 |
        | `context​Definition` | String | API name of the custom context definition that’s sent for context creation. If this property isn’t specified, then the default context definition is used. | Optional | 60.0 |
        | `context​Mapping` | String | Default context mapping of the context definition. If a context mapping is specified, then the API checks whether the mapping belongs to the specified context definition to process the details for hydration. | Optional | 60.0 |
        | `correlation​Id` | String | Unique identifier of the request. | Optional | 60.0 |
        | `currency​Code` | String | Currency code that’s considered for pricing and filtering request. | Optional | 60.0 |
        | `cursor` | String | Unique ID to represent the position of each product in the dataset. | Optional | 60.0 |
        | `enable​Pricing` | Boolean | Indicates whether to enable pricing for the products (`true`) or not (`false`). The default value is `true`. The **Pricing Procedure** toggle from the Product Discovery Settings page from Setup overrides this property. For example, if the **Pricing Procedure** toggle is disabled, then setting the `enablePricing` property to `true` has no effect and the `prices` property in the API response is returned empty. | Optional | 60.0 |
        | `enable​Qualification` | Boolean | Indicates whether to enable qualification rules for the products (`true`) or not (`false`). The default value is `true`. The **Qualification Procedure** toggle from the Product Discovery Settings page from Setup overrides this property. For example, if the **Qualification Procedure** toggle is disabled, then setting the `enableQualification` property to `true` has no effect and the `qualificationContext` property in the API response isn’t returned. | Optional | 60.0 |
        | `execute​ConfigurationRules` | Boolean | Indicates whether to execute configuration rules (`true`) or not (`false`). | Optional | 67.0 |
        | `filter` | [Filter Input](./connect_requests_filter_input.htm.md "Input representation of the request to filter records.") | Filters records based on supported criteria.  The supported property is `name`.  The supported operators are:   - `eq` - `in` - `contains` - `gt`—Specifies a greater than   criteria. Available from API version 63.0 and later for Number, Date, and   Datetime data types only. - `lt`—Specifies a less than   criteria. Available from API version 63.0 and later for Number, Date, and   Datetime data types only. - `gte`—Specifies a greater than   or equal to criteria. Available from API version 63.0 and later for   Number, Date, and Datetime data types only. - `lte`—Specifies a less than or   equal to criteria. Available from API version 63.0 and later for Number,   Date, and Datetime data types only.   If multiple criteria are specified, then the resultant criteria are combined by using the `and` operator. | Optional | 60.0 |
        | `include​CatalogDetails` | Boolean | Indicates whether to include catalog details in the response (`true`) or not (`false`). | Optional | 61.0 |
        | `limit` | Integer | Number of items to include in the response. The default value is 10. | Optional | 60.0 |
        | `offset` | Integer | Reserved for internal use. | Optional | 60.0 |
        | `orderBy` | String[] | Sort order of the results, which is either ascending or descending order. The default sort order is ascending order. The default value is `asc`. | Optional | 60.0 |
        | `priceBookId` | String | ID of the price book to get the prices from. If this property isn’t specified, then prices from the standard price book are fetched. | Optional | 60.0 |
        | `pricingProcedure` | String | API name of the custom pricing procedure that’s used for the pricing process. If this property isn’t specified, then the default pricing procedure is executed. | Optional | 60.0 |
        | `product ClassificationId` | String | ID of the product classification. | Optional | 60.0 |
        | `qualification​Procedure` | String | API name of the custom qualification procedure that’s used for the product qualification process. If this property isn’t specified, then the default qualification procedure is executed. | Optional | 60.0 |
        | `query` | Map<String, Object> | Query to search the products. | Required | 60.0 |
        | `related​ObjectFilter` | [Related Object Filter Input](./connect_requests_related_object_filter_input.htm.md "Input representation of the request to filter records of a related object.")[] | Filter records based on supported criteria for related objects.  The supported object is `ProductSpecificationRecType`.  The supported property is `IsCommerical`.  The supported operator is `eq`.  The supported values are `true` and `false`. | Optional | 60.0 |
        | `searchTerm` | String | String used to get products with the product name containing the search term. See [Search Considerations When Using Indexed Data](https://help.salesforce.com/s/articleView?id=ind.product_catalog_search_considerations.htm&type=5&language=en_US "HTML (New Window)"). | Optional | 62.0 |
        | `transaction​ContextId` | String | ID of the transaction context. | Optional | 66.0 |
        | `transactionId` | String | ID of the transaction. | Optional | 66.0 |
        | `usePromotions` | Boolean | Indicates whether to retrieve eligible promotions from Global Promotion Management (GPM) for each product in the search results (`true`) or not (`false`). If Promotion feature is enabled in the org and this property isn't specified, then the default value is `true`. If the Promotion feature isn't enabled, the default value is `false`. | Optional | 66.0 |
        | `userContext` | [User Context Input](./connect_requests_user_context_input.htm.md "Input representation of the details with the user context.") | User context details. For example, account ID or contact ID. | Optional | 60.0 |

Response body for POST
:   [CPQ Base List](./connect_responses_cpq_base_list_output.htm.md "Output representation of the list of catalogs, categories, or products based on the request.")
