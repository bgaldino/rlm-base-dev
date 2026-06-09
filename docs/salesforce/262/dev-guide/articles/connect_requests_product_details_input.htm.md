---
page_id: connect_requests_product_details_input.htm
title: Product Details Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_product_details_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_requests.htm
fetched_at: 2026-06-09
---

# Product Details Input

Input representation of the request to get product details.

JSON example
:   ```
    {
      "correlationId": "9cbb9650-48c5-11ed-96d1-0afcf185843b",
      "catalogId": "0ZSxx0000000001GAA",
      "priceBookId": "01s26000002ZT71AAG",
      "productSellingModelId": "0jP1Q000000CaVFUA0",
      "userContext": {
        "accountId": "001xx0000000001AAA",
        "contactId": "003xx00000000D7AAI"
      },
      "enablePricing": true,
      "enableQualification": true,
      "qualificationProcedure": "QualificationProcedure",
      "pricingProcedure": "Preview",
      "contextDefinition": "TestDefinition",
      "contextMapping": "TestDefinitionNode",
      "additionalFields": {
        "ProductSellingModelOption": {
          "additionalFields": {
            "ProrationPolicy": {
              "fields": [
                "ArePartialPeriodsAllowed",
                "ProrationPolicyType"
              ]
            }
          }
        },
        "Product2": {
          "fields": [
            "field1",
            "field2"
          ]
        },
        "ProductAttributeDefinition": {
          "fields": [
            "field3",
            "field4"
          ]
        }
      },
      "additionalContextData": [
        {
          "nodeName": "Contract",
          "nodeData": {
            "id": "xxxxx231",
            "name": "Contract1"
          }
        },
        {
          "nodeName": "Lead",
          "nodeData": {
            "id": "lllllll31",
            "name": "Lead1"
          }
        }
      ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `additional​Context​Data` | [Context Data Input](./connect_requests_context_data_input.htm.md "Input representation of the context data.")[] | Additional nodes that are added to the custom or default context definition. The maximum number of supported nodes is 10. | Optional | 60.0 |
    | `additional​Fields` | Map<String, [Additional Fields Input](./connect_requests_additional_fields_input.htm.md "Input representation of the additional standard or custom fields to include in the response.")> | Additional standard or custom fields to include in the response. The supported objects are:   - Product2 - ProductAttributeDefinition—If the fields defined for the   ProductAttributeDefinition object aren’t available for the   ProductClassificationAttr object, then the API request fails.  In API version 66.0 and later, you can request proration policy details in the response for each product selling model option through this property. | Optional | 61.0 |
    | `catalogId` | String | ID of the catalog. If the catalog ID is specified, then the API returns the list of offers from the catalog with the pricing details related to the catalog. | Optional | 60.0 |
    | `context​Definition` | String | API name of the custom context definition that’s sent for context creation. If this property isn’t specified, then the default context definition is used. | Optional | 60.0 |
    | `context​Mapping` | String | Default context mapping of the context definition. If a context mapping is specified, then the API checks whether the mapping belongs to the specified context definition to process the details for hydration. | Optional | 60.0 |
    | `correlation​Id` | String | Unique identifier value that’s attached to the requests and messages, and accepts references to a particular transaction or event chain. | Optional | 60.0 |
    | `currency​Code` | String | Currency code that’s considered for pricing and filtering request. If multiple currencies are enabled for the org, then the currencyCode property is required. | Optional | 60.0 |
    | `enable​Pricing` | Boolean | Indicates whether to enable pricing for the products (`true`) or not (`false`). The default value is `true`. The **Pricing Procedure** toggle from the Product Discovery Settings page from Setup overrides this property. For example, if the **Pricing Procedure** toggle is disabled, then setting the `enablePricing` property to `true` has no effect and the `prices` property in the API response is returned empty. | Optional | 60.0 |
    | `enable​Qualification` | Boolean | Indicates whether to enable qualification rules for the products (`true`) or not (`false`). The default value is `true`. The **Qualification Procedure** toggle from the Product Discovery Settings page from Setup overrides this property. For example, if the **Qualification Procedure** toggle is disabled, then setting the `enableQualification` property to `true` has no effect and the `qualificationContext` property in the API response isn’t returned. | Optional | 60.0 |
    | `priceBook​Id` | String | ID of the price book to fetch the prices from. If this property isn’t specified, then the prices from the standard price book are fetched. | Required | 60.0 |
    | `pricing​Procedure` | String | API name of the custom pricing procedure that’s used for the pricing process. If this property isn’t specified, then the default pricing procedure is executed. | Optional | 60.0 |
    | `product​SellingModel​Id` | String | ID of the product selling model. | Optional | 60.0 |
    | `qualification​Procedure` | String | API name of the custom qualification procedure that’s used for the product qualification process. If this property isn’t specified, then the default qualification procedure is executed. | Optional | 60.0 |
    | `user​Context` | [User Context Input](./connect_requests_user_context_input.htm.md "Input representation of the details with the user context.") | User context details. For example, account ID or contact ID. | Optional | 60.0 |
