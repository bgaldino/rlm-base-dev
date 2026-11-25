---
page_id: connect-requests-product-recommendation-input
title: Product Recommendation Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-product-recommendation-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-api-requests
legacy_page_id: connect_requests_product_recommendation_input.htm
fetched_at: 2026-11-25
---

# Product Recommendation Input

Input representation of the details of a request to get product recommendations.

## JSON Example

```
{
  "currencyCode": "USD",
  "enablePricing": true,
  "enableQualification": true,
  "filter": {
    "criteria": [
      {
        "property": "isActive",
        "operator": "eq",
        "value": true
      },
      {
        "property": "isQualified",
        "operator": "eq",
        "value": true
      }
    ]
  },
  "limit": 12,
  "priceBookId": "01sSG00000DQCjhYAH",
  "transactionId": "0Q0SG0000014Ui50AE"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `additionalContextData` | [Context Data Input](./connect-requests-context-data-input.md)[] | Additional nodes that are added to the custom or default context definition. The maximum number of supported nodes is 10. | Optional | 67.0 |
| `additionalFields` | Map<String, [AdditionalFieldsInputRepresentation](./connect-requests-additional-fields-input.md)> | Additional standard or custom fields of the Product2 object to include in the response. If the requested fields are invalid or access to fields isn’t available, then the API throws an error. | Optional | 67.0 |
| `catalogId` | String | ID of the catalog to fetch the recommended products from. | Optional | 67.0 |
| `contextDefinition` | String | API name of the custom context definition that’s sent for context creation. If you don’t specify this property, then the default context definition is used. | Optional | 67.0 |
| `contextMapping` | String | Default context mapping of the context definition. If you specify a context mapping, then the API checks whether the mapping belongs to the specified context definition to process the details for hydration. | Optional | 67.0 |
| `currencyCode` | String | Currency code that’s considered for pricing and filtering request. If multiple currencies are enabled in the org, then the `currencyCode` property is required. If you don’t specify a currency code, then the value is fetched from the account. | Optional | 67.0 |
| `cursor` | String | Unique ID to represent the position of each product in the data set. | Optional | 67.0 |
| `enablePricing` | Boolean | Indicates whether to enable pricing for products in orgs where Salesforce Pricing is enabled (`true`) or not (`false`). Set the value to `false` to skip the execution of Salesforce Pricing. In orgs where Salesforce Pricing is disabled, you can’t override this value to `true`. The default value is `true`. | Optional | 67.0 |
| `enableQualification` | Boolean | Indicates whether to enable qualification rules for products in orgs where Qualification Procedure is enabled (`true`) or not (`false`). Set the value to `false` to skip the execution of Business Rules Engine qualification rules. In orgs where Qualification Procedure is disabled, you can’t override this value to `true`. The default value is `true`. | Optional | 67.0 |
| `filter` | [Filter Input](./connect-requests-filter-input.md)[] | Filters records based on supported criteria. The supported property is `name`. The supported operators are `eq`, `in`, or `contains`—This value isn’t applicable if the **Use Indexed Data For Product Listing and Search** toggle from the Product Discovery Settings page from Setup is enabled. If you specify multiple criteria, then the resultant criteria are combined by using the `and` operator. | Optional | 67.0 |
| `limit` | Integer | Number of recommended products to include in the response. The default value is `10`. | Optional | 67.0 |
| `priceBookId` | String | ID of the price book to get prices from. If you don’t specify a price book ID, then prices from the standard price book are fetched. | Optional | 67.0 |
| `pricingProcedure` | String | API name of the custom pricing procedure that’s used for the pricing process. If you don’t specify this property, then the default pricing procedure is executed. | Optional | 67.0 |
| `qualificationProcedure` | String | API name of the custom qualification procedure that’s used for the product qualification process. If you don’t specify this property, then the default qualification procedure is executed. | Optional | 67.0 |
| `transactionContextId` | String | ID of the sales transaction context instance. | Optional | 67.0 |
| `transactionId` | String | ID of the quote or order. | Optional | 67.0 |
| `usePromotions` | Boolean | Indicates whether to fetch applicable promotions from Global Promotion Management (GPM) for the guided selection (`true`) or not (`false`). The default value is `false`. | Optional | 67.0 |
| `userContext` | [User Context Input](./connect-requests-user-context-input.md)[] | User context details. For example, account ID or contact ID. | Optional | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-product-recommendation-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
