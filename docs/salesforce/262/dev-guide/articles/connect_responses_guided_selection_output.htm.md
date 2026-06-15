---
page_id: connect_responses_guided_selection_output.htm
title: Guided Selection
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_guided_selection_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_responses.htm
fetched_at: 2026-06-09
---

# Guided Selection

Output representation of the details of a guided selection.

JSON example
:   ```
    {
      "apiStatus": {
        "messages": [],
        "statusCode": "FETCHED_DETAILS_SUCCESSFULLY"
      },
      "correlationId": "corrId",
      "cursor": "MTAwMDAwMDAwNg==",
      "searchTerms": [
        {
          "term": "IPhone"
        },
        {
          "term": "4GB"
        },
        {
          "term": "64GB"
        }
      ],
      "result": [
        {
          "additionalFields": {
            "CustomField1__c": "TextValue",
            "CustomField2__c": "10",
            "StandardField1": "false"
          },
          "description": "IPhone-13",
          "id": "01txx0000006kYwAAI",
          "name": "Sample product 1",
          "prices": [
            {
              "price": 150,
              "priceBookEntryId": "12Axx0000004DF7EAM",
              "priceBookId": "01sxx0000005puLAAQ",
              "pricingModel": {
                "frequency": "Monthly",
                "id": "12Bxx000000CiCDEA0",
                "name": "IPhone-13",
                "occurrence": 6,
                "pricingModelType": "Recurring"
              }
            },
            {
              "price": 400,
              "priceBookEntryId": "12Axx0000004DGjEAM",
              "priceBookId": "01sxx0000005puLAAQ",
              "pricingModel": {
                "id": "12Bxx000000CiCCEA0",
                "name": "IPhone-13",
                "pricingModelType": "OneTime"
              }
            }
          ],
          "qualificationContext": {
            "isQualified": true
          }
        }
      ]
    }
    ```

    This example shows a sample response with details of eligible
    promotions.

    ```
    {
      "apiStatus": {
        "messages": [],
        "statusCode": "FETCHED_DETAILS_SUCCESSFULLY"
      },
      "correlationId": "corrId",
      "cursor": "MTAwMDAwMDAwNg==",
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
      "result": [
        {
          "additionalFields": {
            "CustomField1__c": "TextValue",
            "CustomField2__c": "10",
            "StandardField1": "false"
          },
          "description": "IPhone-13",
          "id": "01txx0000006kYwAAI",
          "name": "Sample product 1",
          "prices": [
            {
              "price": 150,
              "priceBookEntryId": "12Axx0000004DF7EAM",
              "priceBookId": "01sxx0000005puLAAQ",
              "pricingModel": {
                "frequency": "Monthly",
                "id": "12Bxx000000CiCDEA0",
                "name": "IPhone-13",
                "occurrence": 6,
                "pricingModelType": "Recurring"
              }
            },
            {
              "price": 400,
              "priceBookEntryId": "12Axx0000004DGjEAM",
              "priceBookId": "01sxx0000005puLAAQ",
              "pricingModel": {
                "id": "12Bxx000000CiCCEA0",
                "name": "IPhone-13",
                "pricingModelType": "OneTime"
              }
            }
          ],
          "qualificationContext": {
            "isQualified": true
          },
          "eligiblePromotions": [
            {
              "id": "0ZPxx0000000001AAA",
              "name": "IPhone_Promotion_2025",
              "displayName": "iPhone Special Offer",
              "description": "Get 15% off on iPhone 13",
              "priority": 100,
              "startDateTime": "2025-03-01T00:00:00Z",
              "endDateTime": "2025-03-31T23:59:59Z",
              "isAutomatic": true,
              "isCategoryPromo": false,
              "isProductPromo": true,
              "couponCode": null,
              "termsAndConditions": "Valid on iPhone 13 models only."
            },
            {
              "id": "0ZPxx0000000002AAA",
              "name": "Memory_Upgrade_Deal",
              "displayName": "Free Memory Upgrade",
              "description": "Upgrade to 128GB for the price of 64GB",
              "priority": 90,
              "startDateTime": "2025-02-01T00:00:00Z",
              "endDateTime": "2025-12-31T23:59:59Z",
              "isAutomatic": false,
              "isCategoryPromo": false,
              "isProductPromo": true,
              "couponCode": "MEMORY128",
              "termsAndConditions": "Applies to select iPhone models."
            }
          ]
        }
      ]
    }
    ```
:   This example shows a sample request to run visibility
    rules.

    ```
    {
      "apiStatus": {
        "messages": [],
        "statusCode": "FetchedDetailsSuccessfully"
      },
      "correlationId": "ef4f324d-b6d9-47ca-9e78-c6ec60ca5b23",
      "cursor": "MTAwMDAwMDAwNg==",
      "offSet": 1,
      "result": [
        {
          "additionalFields": {},
          "attributeCategories": [],
          "catalogs": [
            {
              "customFields": {},
              "id": "0ZSVW000000AhdC4AS",
              "name": "QuantumBit Hardware",
              "numberOfCategories": 11
            }
          ],
          "categories": [
            {
              "catalogId": "0ZSVW000000AhdC4AS",
              "childCategories": [],
              "customFields": {},
              "eligiblePromotions": [],
              "id": "0ZGVW000000IUEC4A4",
              "name": "Memory"
            }
          ],
          "childProducts": [],
          "childVariationIds": [],
          "configurationRules": [
            {
              "details": [
                {
                  "message": "32GB RDIMM disables 128GB LRDIMM"
                }
              ],
              "type": "disable"
            }
          ],
          "configureDuringSale": "Allowed",
          "description": "128GB RDIMM",
          "displayUrl": "/resource/ram_32GB_RDIMM",
          "eligiblePromotions": [],
          "id": "01tVW000003l7v5YAA",
          "isActive": true,
          "isAssetizable": true,
          "isSoldOnlyWithOtherProds": false,
          "name": "128GB LRDIMM",
          "nodeType": "simpleProduct",
          "prices": [
            {
              "currencyIsoCode": "USD",
              "isDefault": true,
              "isDerived": false,
              "isSelected": false,
              "price": 0,
              "priceBookEntryId": "01uVW000000jzfJYAQ",
              "priceBookId": "01sVW0000024PZlYAM",
              "pricingModel": {
                "id": "0jPVW0000001fh42AA",
                "name": "One-Time",
                "pricingModelType": "OneTime"
              }
            }
          ],
          "productClass": "Simple",
          "productClassification": {},
          "productCode": "QB-MEM 128GB",
          "productComponentGroups": [],
          "productSellingModelOptions": [
            {
              "id": "0iOVW00000049xS2AQ",
              "isDefault": true,
              "productId": "01tVW000003l7v5YAA",
              "productSellingModel": {
                "doesAutoRenewByDefault": false,
                "id": "0jPVW0000001fh42AA",
                "name": "One-Time",
                "sellingModelType": "OneTime",
                "status": "Active"
              },
              "productSellingModelId": "0jPVW0000001fh42AA"
            }
          ],
          "productUnitOfMeasures": []
        }
      ],
      "searchTerms": [
        {
          "tags": [],
          "term": "128GB LRDIMM"
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `apiStatus` | [API Status](./connect_responses_api_status_output.htm.md "Output representation of the API status.") | Status of the API request. | Small, 62.0 | 62.0 |
| `correlation​Id` | String | Unique ID of the request. | Small, 62.0 | 62.0 |
| `cursor` | String | Unique ID to represent the position of each product in the dataset. | Small, 62.0 | 62.0 |
| `result` | Any response body | Result that contains the list of products as per the requested resource. | Small, 62.0 | 62.0 |
| `searchTerms` | [Guided Selection Search Term](./connect_responses_guided_selection_search_term_output.htm.md "Output representation of the search term details for a guided selection.")[] | Search terms for the guided selection. | Small, 62.0 | 62.0 |
