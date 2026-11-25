---
page_id: connect-responses-recommended-products-output
title: Recommended Products
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-recommended-products-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-api-responses
legacy_page_id: connect_responses_recommended_products_output.htm
fetched_at: 2026-11-25
---

# Recommended Products

Output representation of the list of recommended products.

## JSON Example

```
{
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
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `additionalFields` | Map<String, Object> | Additional fields of the product. | Small, 67.0 | 67.0 |
| `availabilityDate` | String | Date when the part is used in the product or is made available for sale. | Small, 67.0 | 67.0 |
| `catalogs` | [Catalog](./connect-responses-product-discovery-catalog-output.md)[] | List of the associated catalogs. This property returns the `name` and `id` values only. | Small, 67.0 | 67.0 |
| `categories` | [Category](./connect-responses-product-discovery-category-output.md)[] | List of the associated categories. This property returns the `name` and `id` values only. | Small, 67.0 | 67.0 |
| `configurationRules` | [Product Configuration Rules](./connect-responses-product-configuration-rules-output.md)[] | List of configuration rules of the product. | Small, 67.0 | 67.0 |
| `configureDuringSale` | String | Specifies whether to allow or prevent configuration when a bundle is sold. | Small, 67.0 | 67.0 |
| `description` | String | Description of the product. | Small, 67.0 | 67.0 |
| `discontinuedDate` | String | Date from when the part can’t be used in the product or sold. | Small, 67.0 | 67.0 |
| `displayUrl` | String | Display image URL of the product. | Small, 67.0 | 67.0 |
| `eligiblePromotions` | [Promotion Details](./connect-responses-promotion-output.md)[] | List of applicable promotions of the product. | Small, 67.0 | 67.0 |
| `endOfLifeDate` | String | Date after which a product isn’t supported, ordered, or maintained. | Small, 67.0 | 67.0 |
| `id` | String | ID of the product. | Small, 67.0 | 67.0 |
| `isActive` | Boolean | Indicates whether the product is active (`true`) or not (`false`). | Small, 67.0 | 67.0 |
| `isAssetizable` | Boolean | Indicates whether a product instance remains a customer asset after it’s purchased (`true`) or not (`false`). The default value is `true`. | Small, 67.0 | 67.0 |
| `isComponentRequired` | Boolean | Indicates whether a product component is required (`true`) or not (`false`). | Small, 67.0 | 67.0 |
| `isDefaultComponent` | Boolean | Indicates whether a product component is a default component (`true`) or not (`false`). | Small, 67.0 | 67.0 |
| `isQuantityEditable` | Boolean | Indicates whether the quantity of a product is editable (`true`) or not (`false`). | Small, 67.0 | 67.0 |
| `isSoldOnlyWithOtherProds` | Boolean | Indicates whether a product can be sold only with other products (`true`) or not (`false`). | Small, 67.0 | 67.0 |
| `name` | String | Name of the product. | Small, 67.0 | 67.0 |
| `nodeType` | String | Specifies whether a node is a product node or a product classification node. | Small, 67.0 | 67.0 |
| `prices` | [Product Prices](./connect-responses-product-prices-output.md)[] | Pricing details of a product. | Small, 67.0 | 67.0 |
| `productClassification` | [Product Classification](./connect-responses-product-discovery-product-classification-output.md)[] | Details of the product classification that the product is based on. | Small, 67.0 | 67.0 |
| `productCode` | String | Universal product code that’s used to track the part that’s used in the product. | Small, 67.0 | 67.0 |
| `productQuantity` | [Product Quantity](./connect-responses-product-quantity-output.md)[] | Quantity details of a product. | Small, 67.0 | 67.0 |
| `productSellingModelOptions` | [Product Selling Model Option](./connect-responses-product-discovery-product-selling-model-option-output.md)[] | Details of the product selling model options. | Small, 67.0 | 67.0 |
| `productSpecificationType` | [Product Specification Type](./connect-responses-product-discovery-product-specification-type-output.md)[] | Details of the product specification type. | Small, 67.0 | 67.0 |
| `productType` | String | Details about the product type. | Small, 67.0 | 67.0 |
| `qualificationContext` | [Qualification Context](./connect-responses-qualification-context-output.md)[] | Context details of a user, which are used for qualification rules. | Small, 67.0 | 67.0 |
| `status` | String | Status of the product, such as active or inactive. | Small, 67.0 | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-recommended-products-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
