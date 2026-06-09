---
page_id: connect_requests_guided_selection_input.htm
title: Guided Selection Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_guided_selection_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_requests.htm
fetched_at: 2026-06-09
---

# Guided Selection Input

Input representation of the guided selection details.

JSON example
:   ```
    {
      "correlationId": "corrId",
      "catalogId": "0ZSxx0000000001GAA",
      "priceBookId": "pricebookId",
      "limit": 10,
      "cursor": "MTAwMDAwMDAwNg==",
      "userContext": {
        "accountId": "accId"
      },
      "guidedSelectionResponseId": "ABCxx0000000001GAA",
      "searchTerms": [
        {
          "term": "IPhone",
          "tags": [
            "deviceType",
            "mobile"
          ]
        },
        {
          "term": "4GB",
          "tags": [
            "RAM"
          ]
        },
        {
          "term": "64GB",
          "tags": [
            "Storage"
          ]
        }
      ],
      "enableQualification": true,
      "enablePricing": true,
      "includeCatalogDetails": false
    }
    ```
:   This example shows a sample request to fetch eligible
    promotions.

    ```
    {
      "correlationId": "corrId",
      "catalogId": "0ZSxx0000000001GAA",
      "priceBookId": "pricebookId",
      "limit": 10,
      "cursor": "MTAwMDAwMDAwNg==",
      "userContext": {
        "accountId": "accId"
      },
      "guidedSelectionResponseId": "ABCxx0000000001GAA",
      "searchTerms": [
        {
          "term": "IPhone",
          "tags": [
            "deviceType",
            "mobile"
          ]
        },
        {
          "term": "4GB",
          "tags": [
            "RAM"
          ]
        },
        {
          "term": "64GB",
          "tags": [
            "Storage"
          ]
        }
      ],
      "enableQualification": true,
      "enablePricing": true,
      "includeCatalogDetails": false,
      "transactionContextId": "context123",
      "transactionId": "trans456",
      "usePromotions": true
    }
    ```
:   This example shows a sample request to run visibility
    rules.

    ```
    {
      "catalogId": "0ZSVW000000AhdC4AS",
      "currencyCode": "USD",
      "enablePricing": true,
      "enableQualification": true,
      "executeConfigurationRules": true,
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
      "guidedSelectionResponseId": "0U3VW0000000a1t0AA",
      "includeCatalogDetails": true,
      "limit": 12,
      "offset": 0,
      "orderBy": [
        "name:asc"
      ],
      "priceBookId": "01sVW0000024PZlYAM",
      "transactionId": "0Q0VW000001190f0AA",
      "userContext": {
        "accountId": null
      }
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `additional​ContextData` | [Context Data Input](./connect_requests_context_data_input.htm.md "Input representation of the context data.")[] | Additional nodes that are added to the custom or default context definition. The maximum number of supported nodes is 10. | Optional | 62.0 |
    | `additional​Fields` | Map<String, [Additional Fields Input](./connect_requests_additional_fields_input.htm.md "Input representation of the additional standard or custom fields to include in the response.")> | Additional standard or custom fields of the Product2 object to include in the response.  If the requested fields are invalid or access to fields isn’t available, then the API throws an error. | Optional | 62.0 |
    | `catalog​Id` | String | ID of the catalog. | Required | 62.0 |
    | `category​Id` | String | ID of the category. | Optional | 62.0 |
    | `context​Definition` | String | API name of the custom context definition that’s sent for context creation. If this property isn’t specified, then the default context definition is used. | Optional | 62.0 |
    | `context​Mapping` | String | Default context mapping of the context definition. If a context mapping is specified, then the API checks whether the mapping belongs to the specified context definition to process the details for hydration. | Optional | 62.0 |
    | `correlation​Id` | String | Unique identifier value that’s attached to the requests and messages, and accepts references to a particular transaction or event chain. | Optional | 62.0 |
    | `currency​Code` | String | Currency code that’s considered for pricing and filtering request. If multiple currencies are enabled for the org, then the `currencyCode` property is required. | Optional | 62.0 |
    | `cursor` | String | Unique ID to represent the position of each product in the dataset. | Optional | 62.0 |
    | `enable​Pricing` | Boolean | Indicates whether to enable pricing for the products (`true`) or not (`false`). The default value is `true`. | Optional | 62.0 |
    | `enable​Qualification` | Boolean | Indicates whether to enable qualification rules for the products (`true`) or not (`false`). The default value is `true`. | Optional | 62.0 |
    | `execute​ConfigurationRules` | Boolean | Indicates whether to execute configuration rules (`true`) or not (`false`). | Optional | 67.0 |
    | `filter` | [Filter Input](./connect_requests_filter_input.htm.md "Input representation of the request to filter records.") | Filters records based on supported criteria.  The supported property is `name`.  The supported operators are:   - `eq` - `in` - `contains`—This value isn't   applicable if the **Use Indexed Data For Product Listing and   Search** toggle from the Product Discovery Settings page from   Setup is enabled.   If multiple criteria are specified, then the resultant criteria are combined by using the `and` operator. | Optional | 62.0 |
    | `guided​Selection​ResponseId` | String | Response identifier of the guided selection. | Required if the `searchTerms` property isn’t specified. | 62.0 |
    | `include​Catalog​Details` | Boolean | Indicates whether to include catalog details in the response (`true`) or not (`false`). | Optional | 62.0 |
    | `limit` | Integer | Number of items to include in the response. The default value is 10. | Optional | 62.0 |
    | `order​By` | String[] | Sort order of the results, which is either ascending (`asc`) or descending order (`desc`). The default sort order is ascending order. The default value is `asc`.  If the **Use Indexed Data For Product Listing and Search** toggle from the Product Discovery Settings page from Setup is enabled, then you can sort products by using name only. | Optional | 62.0 |
    | `price​BookId` | String | ID of the price book to get the prices from. If this property isn’t specified, then prices from the standard price book are fetched. | Required | 62.0 |
    | `pricing​Procedure` | String | API name of the custom pricing procedure that’s used for the pricing process. If this property isn’t specified, then the default pricing procedure is executed. | Optional | 62.0 |
    | `product​Classification​Id` | String | ID of the product classification. | Optional | 62.0 |
    | `qualification​Procedure` | String | API name of the custom qualification procedure that’s used for the product qualification process. If this property isn’t specified, then the default qualification procedure is executed. | Optional | 62.0 |
    | `searchTerms` | [Guided Selection Search Term Input](./connect_requests_guided_selection_search_term_input.htm.md "Input representation of the search terms of a guided selection.")[] | Search terms of the guided selection. | Required if the `guided​Selection​ResponseId` property isn’t specified. | 62.0 |
    | `transaction​ContextId` | String | ID of the transaction context. | Optional | 67.0 |
    | `transactionId` | String | ID of the transaction. | Optional | 67.0 |
    | `usePromotions` | Boolean | Indicates whether to fetch applicable promotions from Global Promotion Management (GPM) for the guided selection (`true`) or not (`false`). If Promotion feature is enabled in the org and this property isn't specified, then the default value is `true`. If the Promotion feature isn't enabled, the default value is `false`. | Optional | 66.0 |
    | `user​Context` | [User Context Input](./connect_requests_user_context_input.htm.md "Input representation of the details with the user context.") | User context details. For example, account ID or contact ID. | Optional | 62.0 |

    If both the `guided​Selection​ResponseId` and
    `searchTerms` properties are specified, then the
    `searchTerms` property is considered in the input
    request.
