---
page_id: connect_requests_product_list_input.htm
title: Product List Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_product_list_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_requests.htm
fetched_at: 2026-06-09
---

# Product List Input

Input representation of the request to retrieve a list of products.

JSON example
:   ```
    {
      "correlationId": "eeaa1db2-f371-4227-a886-c77e2f66ce1d",
      "limit": 60,
      "cursor": "MTAwMDAwMDAwNg==",
      "orderBy": [
        "name:asc"
      ],
      "catalogId": "0ZSDU0000002Og74AE",
      "categoryId": "0ZGDU0000002P0H4AU",
      "priceBookId": "01sDU000000JVsVYAW",
      "productClassificationId": "11BDU0000002TCC2A2",
      "currencyCode": "USD",
      "userContext": {
        "accountId": "001DU000001o2UzYAI"
      },
      "includeCatalogDetails": true,
      "enableQualification": true,
      "enablePricing": true,
      "qualificationProcedure": "ProductQualification",
      "pricingProcedure": "pricingProcedure",
      "contextDefinition": "BrowseContextDefinitionExt",
      "contextMapping": "ProductDiscoveryMapping",
      "filter": {
        "criteria": [
          {
            "property": "name",
            "operator": "eq",
            "value": "Laptop Pro Bundle"
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
              "value": true
            }
          ]
        }
      ],
      "additionalContextData": [
        {
          "nodeName": "Account",
          "nodeData": {
            "id": "001DU000001o2UzYAI",
            "name": "Cloud Kicks"
          }
        }
      ],
      "additionalFields": {
        "Product2": {
          "fields": [
            "CanRamp",
            "DecompositionScope",
            "ProductCode"
          ]
        }
      }
    }
    ```

    If a parent category ID is specified in the request body, then the API
    returns all products associated to all child categories.
:   This example shows a sample request to retrieve a product list with promotions.
:   ```
    {
      "correlationId": "eeaa1db2-f371-4227-a886-c77e2f66ce1d",
      "limit": 60,
      "cursor": "MTAwMDAwMDAwNg==",
      "orderBy": [
        "name:asc"
      ],
      "catalogId": "0ZSDU0000002Og74AE",
      "categoryId": "0ZGDU0000002P0H4AU",
      "priceBookId": "01sDU000000JVsVYAW",
      "productClassificationId": "11BDU0000002TCC2A2",
      "currencyCode": "USD",
      "userContext": {
        "accountId": "001DU000001o2UzYAI"
      },
      "includeCatalogDetails": true,
      "enableQualification": true,
      "enablePricing": true,
      "qualificationProcedure": "ProductQualification",
      "pricingProcedure": "pricingProcedure",
      "contextDefinition": "BrowseContextDefinitionExt",
      "contextMapping": "ProductDiscoveryMapping",
      "filter": {
        "criteria": [
          {
            "property": "name",
            "operator": "eq",
            "value": "Laptop Pro Bundle"
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
              "value": true
            }
          ]
        }
      ],
      "additionalContextData": [
        {
          "nodeName": "Account",
          "nodeData": {
            "id": "001DU000001o2UzYAI",
            "name": "Cloud Kicks"
          }
        }
      ],
      "additionalFields": {
        "Product2": {
          "fields": [
            "CanRamp",
            "DecompositionScope",
            "ProductCode"
          ]
        }
      },
      "executeConfigurationRules": false,
      "transactionContextId": "a1b2c3d4e5f6",
      "transactionId": "trans789",
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
      "catalogId": "0ZSVW000000AhdC4AS",
      "limit": 12,
      "offset": 0,
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
    | `additional​ContextData` | [Context Data Input](./connect_requests_context_data_input.htm.md "Input representation of the context data.")[] | Additional nodes that are added to the custom or default context definition. The maximum number of supported nodes is 10. | Optional | 60.0 |
    | `additional​Fields` | Map<String, [Additional Fields Input](./connect_requests_additional_fields_input.htm.md "Input representation of the additional standard or custom fields to include in the response.")> | Additional standard or custom fields of the Product2 object to include in the response.  If the requested fields are invalid or access to fields isn’t available, then the API throws an error. | Optional | 61.0 |
    | `catalog​Id` | String | ID of the catalog. If the catalog ID is specified, then the API returns the list of offers from the catalog with the pricing details related to the catalog. | Optional | 60.0 |
    | `category​Id` | String | ID of the category. If the category ID isn’t specified, then the API returns the list of offers from the catalog. | Optional | 60.0 |
    | `context​Definition` | String | API name of the custom context definition that’s sent for context creation. If this property isn’t specified, then the default context definition is used. | Optional | 60.0 |
    | `context​Mapping` | String | Default context mapping of the context definition. If a context mapping is specified, then the API checks whether the mapping belongs to the specified context definition to process the details for hydration. | Optional | 60.0 |
    | `correlation​Id` | String | Unique identifier of the request. | Optional | 60.0 |
    | `currency​Code` | String | Currency code that’s considered for pricing and filtering request. If multiple currencies are enabled for the org, then the `currencyCode` property is required. | Optional | 60.0 |
    | `cursor` | String | Unique ID to represent the position of each product in the dataset. | Optional | 60.0 |
    | `enable​Pricing` | Boolean | Indicates whether to enable pricing for the products (`true`) or not (`false`). The default value is `true`. The **Pricing Procedure** toggle from the Product Discovery Settings page from Setup overrides this property. For example, if the **Pricing Procedure** toggle is disabled, then setting the `enablePricing` property to `true` has no effect and the `prices` property in the API response is returned empty. | Optional | 60.0 |
    | `enable​Qualification` | Boolean | Indicates whether to enable qualification rules for the products (`true`) or not (`false`). The default value is `true`. The **Qualification Procedure** toggle from the Product Discovery Settings page from Setup overrides this property. For example, if the **Qualification Procedure** toggle is disabled, then setting the `enableQualification` property to `true` has no effect and the `qualificationContext` property in the API response isn’t returned. | Optional | 60.0 |
    | `execute​ConfigurationRules` | Boolean | Indicates whether to execute configuration rules (`true`) or not (`false`). | Optional | 67.0 |
    | `filter` | [Filter Input](./connect_requests_filter_input.htm.md "Input representation of the request to filter records.") | Filters records based on supported criteria.  The supported property is `name`.  The supported operators are:   - `eq` - `in` - `contains`—This value isn't   applicable if the **Use Indexed Data For Product Listing and   Search** toggle from the Product Discovery Settings page from   Setup is enabled.   If multiple criteria are specified, then the resultant criteria are combined by using the `and` operator. | Optional | 60.0 |
    | `include​Catalog​Details` | Boolean | Indicates whether to include catalog details in the response (`true`) or not (`false`). | Optional | 61.0 |
    | `limit` | Integer | Number of items to include in the response. The default value is 10. | Optional | 60.0 |
    | `offset` | Integer | Reserved for internal use. | Optional | 60.0 |
    | `order​By` | String[] | Sort order of the results, which is either ascending (`asc`) or descending order (`desc`). The default sort order is ascending order. The default value is `asc`.  If the **Use Indexed Data For Product Listing and Search** toggle from the Product Discovery Settings page from Setup is enabled, then you can sort products by using name only. | Optional | 60.0 |
    | `price​BookId` | String | ID of the price book to get the prices from. If this property isn’t specified, then prices from the standard price book are fetched. | Required | 60.0 |
    | `pricing​Procedure` | String | API name of the custom pricing procedure that’s used for the pricing process. If this property isn’t specified, then the default pricing procedure is executed. | Optional | 60.0 |
    | `product​Classification​Id` | String | ID of the product classification. | Optional | 60.0 |
    | `qualification​Procedure` | String | API name of the custom qualification procedure that’s used for the product qualification process. If this property isn’t specified, then the default qualification procedure is executed. | Optional | 60.0 |
    | `related​Object​Filters` | [Related Object Filter Input](./connect_requests_related_object_filter_input.htm.md "Input representation of the request to filter records of a related object.")[] | Filter records based on supported criteria for related objects.  The supported object is `ProductSpecificationRecType`.  The supported property is `IsCommerical`.  The supported operator is `eq`.  The supported values are `true` and `false`. | Optional | 60.0 |
    | `transaction​ContextId` | String | ID of the transaction context. | Optional | 67.0 |
    | `transactionId` | String | ID of the transaction. | Optional | 67.0 |
    | `usePromotions` | Boolean | Indicates whether to fetch applicable promotions from Global Promotion Management (GPM) for each product in the list (`true`) or not (`false`). If Promotion feature is enabled in the org and this property isn't specified, then the default value is `true`. If the Promotion feature isn't enabled, the default value is `false`. | Optional | 66.0 |
    | `user​Context` | [User Context Input](./connect_requests_user_context_input.htm.md "Input representation of the details with the user context.") | User context details. For example, account ID or contact ID. | Optional | 60.0 |
