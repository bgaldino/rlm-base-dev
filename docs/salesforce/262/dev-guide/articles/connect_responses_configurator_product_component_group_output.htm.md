---
page_id: connect_responses_configurator_product_component_group_output.htm
title: Configurator Product Component Group
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_configurator_product_component_group_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Configurator Product Component Group

Output representation of the product component group in a product
classification.

JSON example
:   ```
        "productComponentGroups": [
          {
            "classifications": [],
            "code": "SERVICE",
            "components": [
              {
                "additionalFields": [],
                "attributeCategories": [],
                "description": "Introducing the Cisco Rack Server NX44 Service, a comprehensive protection plan designed to safeguard your valuable data infrastructure. With extended coverage and rapid response times, this warranty ensures peace of mind and uninterrupted performance for your critical business operations.",
                "id": "01txx0000006jmWAAQ",
                "isActive": true,
                "isAssetizable": true,
                "isComponentRequired": false,
                "isConfigurable": false,
                "isDefaultComponent": false,
                "isQuantityEditable": false,
                "isSoldOnlyWithOtherProds": false,
                "name": "Cisco Rack Server Service - 1 Year",
                "nodeType": "simpleProduct",
                "prices": [],
                "productClassification": {},
                "productCode": "SERVICE",
                "productComponentGroups": [],
                "productRelatedComponent": {
                  "childProductId": "01txx0000006jmWAAQ",
                  "childSellingModelId": "0jPxx000000004rEAA",
                  "doesBundlePriceIncludeChild": true,
                  "id": "0dSxx000000001dEAA",
                  "isComponentRequired": false,
                  "isDefaultComponent": false,
                  "isQuantityEditable": false,
                  "parentProductId": "01txx0000006jkuAAA",
                  "parentSellingModelId": "0jPxx000000004rEAA",
                  "productComponentGroupId": "0y7xx000000001dAAA",
                  "productRelationshipTypeId": "0yoxx00000001IfAAI",
                  "quantity": 1,
                  "quantityScaleMethod": "Proportional"
                },
                "productSellingModelOptions": [
                  {
                    "id": "0iOxx000000009hEAA",
                    "productId": "01txx0000006jmWAAQ",
                    "productSellingModel": {
                      "id": "0jPxx000000004rEAA",
                      "name": "Termed Annually",
                      "pricingTerm": 1,
                      "pricingTermUnit": "Annual",
                      "sellingModelType": "TermDefined",
                      "status": "Active"
                    },
                    "productSellingModelId": "0jPxx000000004rEAA"
                  },
                  {
                    "id": "0iOxx00000000PpEAI",
                    "productId": "01txx0000006jmWAAQ",
                    "productSellingModel": {
                      "id": "0jPxx0000000085EAA",
                      "name": "Evergreen Annually",
                      "pricingTerm": 1,
                      "pricingTermUnit": "Annual",
                      "sellingModelType": "Evergreen",
                      "status": "Active"
                    },
                    "productSellingModelId": "0jPxx0000000085EAA"
                  }
                ]
              }
            ],
            "description": "The services available for the Cisco Server Rack NX44 product provide comprehensive coverage and support for optimal performance and reliability, ensuring peace of mind for your data center infrastructure.",
            "id": "0y7xx000000001dAAA",
            "maxBundleComponents": 1,
            "minBundleComponents": 0,
            "name": "Services",
            "parentProductId": "01txx0000006jkuAAA",
            "sequence": 1
          },
          {
            "classifications": [],
            "code": "WARRANTY",
            "components": [
              {
                "additionalFields": [],
                "attributeCategories": [],
                "description": "Introducing the Cisco Rack Server NX44 Warranty, a comprehensive protection plan designed to safeguard your valuable data infrastructure. With extended coverage and rapid response times, this warranty ensures peace of mind and uninterrupted performance for your critical business operations.",
                "id": "01txx0000006jjIAAQ",
                "isActive": true,
                "isAssetizable": true,
                "isComponentRequired": false,
                "isConfigurable": false,
                "isDefaultComponent": true,
                "isQuantityEditable": true,
                "isSoldOnlyWithOtherProds": false,
                "name": "Cisco Rack Server Warranty - 1 Year",
                "nodeType": "simpleProduct",
                "prices": [],
                "productClassification": {},
                "productCode": "WARRANTY",
                "productComponentGroups": [],
                "productRelatedComponent": {
                  "childProductId": "01txx0000006jjIAAQ",
                  "childSellingModelId": "0jPxx000000001dEAA",
                  "doesBundlePriceIncludeChild": false,
                  "id": "0dSxx0000000001EAA",
                  "isComponentRequired": false,
                  "isDefaultComponent": true,
                  "isQuantityEditable": true,
                  "maxQuantity": 1,
                  "parentProductId": "01txx0000006jkuAAA",
                  "parentSellingModelId": "0jPxx000000001dEAA",
                  "productComponentGroupId": "0y7xx0000000001AAA",
                  "productRelationshipTypeId": "0yoxx00000001IfAAI",
                  "quantity": 1,
                  "quantityScaleMethod": "Proportional",
                  "sequence": 0
                },
                "productSellingModelOptions": [
                  {
                    "id": "0iOxx000000001dEAA",
                    "productId": "01txx0000006jjIAAQ",
                    "productSellingModel": {
                      "id": "0jPxx000000001dEAA",
                      "name": "One Time",
                      "sellingModelType": "OneTime",
                      "status": "Active"
                    },
                    "productSellingModelId": "0jPxx000000001dEAA"
                  },
                  {
                    "id": "0iOxx00000000HlEAI",
                    "productId": "01txx0000006jjIAAQ",
                    "productSellingModel": {
                      "id": "0jPxx000000003FEAQ",
                      "name": "Termed Monthly",
                      "pricingTerm": 1,
                      "pricingTermUnit": "Months",
                      "sellingModelType": "TermDefined",
                      "status": "Active"
                    },
                    "productSellingModelId": "0jPxx000000003FEAQ"
                  },
                  {
                    "id": "0iOxx00000000JNEAY",
                    "productId": "01txx0000006jjIAAQ",
                    "productSellingModel": {
                      "id": "0jPxx000000004rEAA",
                      "name": "Termed Annually",
                      "pricingTerm": 1,
                      "pricingTermUnit": "Annual",
                      "sellingModelType": "TermDefined",
                      "status": "Active"
                    },
                    "productSellingModelId": "0jPxx000000004rEAA"
                  },
                  {
                    "id": "0iOxx00000000KzEAI",
                    "productId": "01txx0000006jjIAAQ",
                    "productSellingModel": {
                      "id": "0jPxx0000000085EAA",
                      "name": "Evergreen Annually",
                      "pricingTerm": 1,
                      "pricingTermUnit": "Annual",
                      "sellingModelType": "Evergreen",
                      "status": "Active"
                    },
                    "productSellingModelId": "0jPxx0000000085EAA"
                  },
                  {
                    "id": "0iOxx00000000MbEAI",
                    "productId": "01txx0000006jjIAAQ",
                    "productSellingModel": {
                      "id": "0jPxx000000006TEAQ",
                      "name": "Evergreen Monthly",
                      "pricingTerm": 1,
                      "pricingTermUnit": "Months",
                      "sellingModelType": "Evergreen",
                      "status": "Active"
                    },
                    "productSellingModelId": "0jPxx000000006TEAQ"
                  }
                ]
              }
            ],
            "description": "The warranties available for the Cisco Server Rack NX44 product provide comprehensive coverage and support for optimal performance and reliability, ensuring peace of mind for your data center infrastructure.",
            "id": "0y7xx0000000001AAA",
            "maxBundleComponents": 1,
            "minBundleComponents": 0,
            "name": "Warranties",
            "parentProductId": "01txx0000006jkuAAA",
            "sequence": 0
          }
        ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `classifications` | [Configurator Product Classification](./connect_responses_configurator_product_classification_output.htm.md "Output representation of the product classification in a product configuration.")[] | List of classifications for this product component group. | Small, 60.0 | 60.0 |
| `code` | String | Code of the product component group. | Small, 60.0 | 60.0 |
| `components` | [Configurator Product Catalog](./connect_responses_configurator_product_catalog_output.htm.md "Output representation of the product catalog.")[] | Components within the product component group. | Small, 60.0 | 60.0 |
| `description` | String | Description of the product component group. | Small, 60.0 | 60.0 |
| `id` | String | ID of the product component group. | Small, 60.0 | 60.0 |
| `maxBundle​Components` | Integer | Maximum number of bundle components within the product component group. | Small, 60.0 | 60.0 |
| `minBundle​Components` | Integer | Minimum number of bundle components within the product component group. | Small, 60.0 | 60.0 |
| `name` | String | Name of the product component group. | Small, 60.0 | 60.0 |
| `parent​ProductId` | String | Parent Product2 ID of the product component group. | Small, 60.0 | 60.0 |
| `sequence` | Integer | Sequence of the product component group. | Small, 60.0 | 60.0 |
