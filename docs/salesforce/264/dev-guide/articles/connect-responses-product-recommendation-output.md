---
page_id: connect-responses-product-recommendation-output
title: Product Recommendations
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-recommendation-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-api-responses
legacy_page_id: connect_responses_product_recommendation_output.htm
fetched_at: 2026-11-25
---

# Product Recommendations

Output representation of the fetched product recommendations.

## JSON Example

```
{
  "cursor": "MTAwMDAwMDAwNQ==",
  "errors": [],
  "products": [
    {
      "additionalFields": {},
      "catalogs": [
        {
          "customFields": {},
          "id": "0ZSSG000001875O4AQ",
          "name": "Hardware Catalog",
          "numberOfCategories": 4
        }
      ],
      "categories": [
        {
          "catalogId": "0ZSSG000001875O4AQ",
          "childCategories": [],
          "customFields": {},
          "eligiblePromotions": [],
          "id": "0ZGSG000001DJtv4AG",
          "name": "Accessories",
          "qualificationContext": {
            "isQualified": true
          }
        }
      ],
      "configurationRules": [
        {
          "details": [
            {
              "message": "recommend Mouse from monitor"
            }
          ],
          "type": "recommend"
        }
      ],
      "configureDuringSale": "Allowed",
      "description": "HeyMicky Mouse compatible comes with choice of USB or Wireless connectivity.",
      "displayUrl": "https://5.imimg.com/data5/IS/JP/MY-58678879/computer-mouse.jpg",
      "eligiblePromotions": [],
      "id": "01tSG00000BiywkYAB",
      "isActive": true,
      "isAssetizable": true,
      "isSoldOnlyWithOtherProds": false,
      "name": "Mouse",
      "nodeType": "simpleProduct",
      "prices": [
        {
          "currencyIsoCode": "USD",
          "isDefault": true,
          "isDerived": false,
          "isSelected": false,
          "price": 7.99,
          "priceBookEntryId": "01uSG000004wTsEYAU",
          "priceBookId": "01sSG00000DQCjhYAH",
          "pricingModel": {
            "id": "0jPSG000000Avcv2AC",
            "name": "One Time",
            "pricingModelType": "OneTime"
          }
        }
      ],
      "productClassification": {
        "id": "11BSG00000UNijx2AD"
      },
      "productCode": "MOU001",
      "productSellingModelOptions": [
        {
          "id": "0iOSG000000J64x2AC",
          "isDefault": true,
          "productId": "01tSG00000BiywkYAB",
          "productSellingModel": {
            "doesAutoRenewByDefault": false,
            "id": "0jPSG000000Avcv2AC",
            "name": "One Time",
            "sellingModelType": "OneTime",
            "status": "Active"
          },
          "productSellingModelId": "0jPSG000000Avcv2AC"
        }
      ],
      "productSpecificationType": {
        "name": "Commercial",
        "productSpecificationRecordType": {}
      },
      "qualificationContext": {
        "isQualified": true
      }
    }
  ],
  "success": true,
  "transactionContextId": "0000000p18dq18g002917732061529307c5e047346664b2f81ff3d4845acf2d0"
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `cursor` | String | Unique ID to represent the position of each product in the data set. | Small, 67.0 | 67.0 |
| `errors` | [Product Recommendation Errors](./connect-responses-product-recommendation-errors-output.md)[] | List of errors encountered during the processing of the API request. | Small, 67.0 | 67.0 |
| `products` | [Recommended Products](./connect-responses-recommended-products-output.md)[] | List of recommended products. | Small, 67.0 | 67.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 67.0 | 67.0 |
| `transactionContextId` | String | ID of the sales transaction context. | Small, 67.0 | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-recommendation-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
