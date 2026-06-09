---
page_id: connect_responses_cpq_base_list_output.htm
title: CPQ Base List
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_cpq_base_list_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_responses.htm
fetched_at: 2026-06-09
---

# CPQ Base List

Output representation of the list of catalogs, categories, or products based on the
request.

JSON example
:   This example shows a sample catalog list.
:   ```
    {
      "apiStatus": {
        "messages": [
          
        ],
        "statusCode": "FetchedDetailsSuccessfully"
      },
      "correlationId": "9f417514-9587-4063-9e48-18a2cf2477c0",
      "limit": 10,
      "offSet": 0,
      "query": {
        
      },
      "result": [
        {
          "catalogCode": "Mobiles",
          "catalogType": "Sales",
          "description": "Catalog for mobile phones",
          "effectiveEndDate": "2028-04-01T19:00Z",
          "effectiveStartDate": "2024-04-01T19:00Z",
          "id": "0ZSxx0000000001GAA",
          "name": "Mobiles",
          "numberOfCategories": 3
        }
      ],
      "total": 1
    }
    ```
:   This example shows a sample category list.
:   ```
    {
      "apiStatus": {
        "messages": [
          
        ],
        "statusCode": "FetchedDetailsSuccessfully"
      },
      "correlationId": "3f2a8f45-e7d2-42ec-bc4c-b981d750e912",
      "query": {
        
      },
      "result": [
        {
          "catalogId": "0ZSxx0000000001GAA",
          "childCategories": [
            
          ],
          "description": "Category for Apple phones and iPads",
          "id": "0ZGxx0000000001GAA",
          "name": "Apple",
          "sortOrder": 1,
          "isNavigational": true
        },
        {
          "catalogId": "0ZSxx0000000001GAA",
          "childCategories": [
            
          ],
          "description": "Category for Samsung phones",
          "id": "0ZGxx000000004rGAA",
          "name": "Samsung",
          "sortOrder": 2,
          "isNavigational": true
        },
        {
          "catalogId": "0ZSxx0000000001GAA",
          "childCategories": [
            
          ],
          "description": "Category for Android phones",
          "id": "0ZGxx000000006TGAQ",
          "name": "Android",
          "isNavigational": true
        }
      ],
      "total": 3
    }
    ```
:   This example shows a sample product list.
:   ```
    {
      "apiStatus": {
        "messages": [],
        "statusCode": "FetchedDetailsSuccessfully"
      },
      "contextId": "f36f8e73f1fc338cc4e93c61613cba07a6a0129941d97e5dd6e52a2885776ce4",
      "correlationId": "eeaa1db2-f371-4227-a886-c77e2f66ce1d",
      "cursor": "MTAwMDAwMDAwNg==",
      "query": {},
      "result": [
        {
          "additionalFields": {
            "DecompositionScope": "OrderLineItem",
            "ProductCode": "LPB001",
            "CanRamp": false
          },
          "attributeCategories": [],
          "catalogs": [
            {
              "customFields": {},
              "id": "0ZSDU0000002Og74AE",
              "name": "Service Catalog",
              "numberOfCategories": 5
            }
          ],
          "categories": [
            {
              "catalogId": "0ZSDU0000002Og74AE",
              "childCategories": [],
              "customFields": {},
              "hasSubCategories": false,
              "id": "0ZGDU0000002P0H4AU",
              "name": "Cloud Services",
              "qualificationContext": {
                "isQualified": true
              }
            }
          ],
          "childProducts": [],
          "configureDuringSale": "Allowed",
          "description": "The laptop pro bundle includes a Laptop, mouse, warranty for 2 years, premium support and printer bundle",
          "displayUrl": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCrGjPR1fvJqg4yP3RMyqjI0H9eL6tk1fvzw&amp;usqp=CAU",
          "id": "01tDU000000ExkZYAS",
          "isActive": true,
          "isAssetizable": true,
          "isSoldOnlyWithOtherProds": false,
          "name": "Laptop Pro Bundle",
          "nodeType": "bundleProduct",
          "prices": [],
          "productClassification": {},
          "productCode": "LPB001",
          "productComponentGroups": [],
          "productSellingModelOptions": [
            {
              "id": "0iODU0000002TBN2A2",
              "productId": "01tDU000000ExkZYAS",
              "productSellingModel": {
                "id": "0jPDU0000002OTv2AM",
                "name": "One Time",
                "sellingModelType": "OneTime",
                "status": "Active"
              },
              "productSellingModelId": "0jPDU0000002OTv2AM"
            }
          ],
          "productSpecificationType": {
            "name": "Commercial",
            "productSpecificationRecordType": {}
          },
          "productType": "Bundle",
          "qualificationContext": {
            "isQualified": true
          }
        }
      ]
    }
    ```
:   This example shows a sample of the list of products retrieved based on the `Laptop` search term.
:   ```
    {
      "apiStatus": {
        "messages": [],
        "statusCode": "FetchedDetailsSuccessfully"
      },
      "correlationId": "d9d8f898-19f5-464a-ba2b-6a070783f6c4",
      "cursor": "MTAwMDAwMDAwMw==",
      "facets": [
        {
          "attributeType": "ProductStandard",
          "displayName": "Product Type",
          "displayRank": 2,
          "nameOrId": "Type",
          "values": [
            {
              "displayName": "Bundle",
              "nameOrId": "Bundle"
            }
          ]
        },
        {
          "attributeType": "ProductDynamicAttribute",
          "displayName": "Display",
          "displayRank": 3,
          "nameOrId": "0tjDU0000003K5BYAU",
          "values": [
            {
              "displayName": "1080p Built-in Display",
              "nameOrId": "1080p Built-in Display"
            },
            {
              "displayName": "2k Built-in Display",
              "nameOrId": "2k Built-in Display"
            },
            {
              "displayName": "4k Built-in Display",
              "nameOrId": "4k Built-in Display"
            }
          ]
        }
      ],
      "limit": 10,
      "query": {},
      "result": [
        {
          "additionalFields": {},
          "attributeCategories": [],
          "catalogs": [],
          "categories": [
            {
              "catalogId": "0ZSDU0000002Og64AE",
              "childCategories": [],
              "customFields": {},
              "hasSubCategories": false,
              "id": "0ZGDU0000002P0A4AU",
              "name": "Laptops",
              "qualificationContext": {
                "isQualified": true
              }
            }
          ],
          "configureDuringSale": "Allowed",
          "description": "Battery- or AC-powered personal computer (PC) smaller than a briefcase",
          "displayUrl": "https://media.istockphoto.com/id/1023428598/photo/3d-illustration-laptop-isolated-on-white-background-laptop-with-empty-space-screen-laptop-at.jpg?s=612x612&amp;w=0&amp;k=20&amp;c=ssK6er5v1fGpSghGiqySwoD8tn5blC7xgefQJI2xU38=",
          "id": "01tDU000000ExkWYAS",
          "isActive": true,
          "isAssetizable": true,
          "isSoldOnlyWithOtherProds": false,
          "name": "Laptop",
          "nodeType": "simpleProduct",
          "prices": [],
          "productClassification": {
            "id": "11BDU0000002TCD2A2"
          },
          "productCode": "LP001",
          "productComponentGroups": [],
          "productSellingModelOptions": [
            {
              "id": "0iODU0000002TBF2A2",
              "productId": "01tDU000000ExkWYAS",
              "productSellingModel": {
                "id": "0jPDU0000002OTv2AM",
                "name": "One Time",
                "sellingModelType": "OneTime",
                "status": "Active"
              },
              "productSellingModelId": "0jPDU0000002OTv2AM"
            }
          ],
          "productSpecificationType": {
            "name": "Commercial",
            "productSpecificationRecordType": {}
          },
          "qualificationContext": {
            "isQualified": true
          }
        },
        {
          "additionalFields": {},
          "attributeCategories": [],
          "catalogs": [],
          "categories": [
            {
              "catalogId": "0ZSDU0000002Og64AE",
              "childCategories": [],
              "customFields": {},
              "hasSubCategories": false,
              "id": "0ZGDU0000002P0A4AU",
              "name": "Laptops",
              "qualificationContext": {
                "isQualified": true
              }
            }
          ],
          "configureDuringSale": "Allowed",
          "description": "The laptop basic bundle includes a Laptop, mouse, and warranty for 1 year.",
          "displayUrl": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTbf49JG4zZogCmZMJuXU38qOkR9X36MN4bSw&amp;usqp=CAU",
          "id": "01tDU000000ExkXYAS",
          "isActive": true,
          "isAssetizable": true,
          "isSoldOnlyWithOtherProds": false,
          "name": "Laptop Basic Bundle",
          "nodeType": "bundleProduct",
          "prices": [],
          "productClassification": {},
          "productCode": "LB001",
          "productComponentGroups": [],
          "productSellingModelOptions": [
            {
              "id": "0iODU0000002TBD2A2",
              "productId": "01tDU000000ExkXYAS",
              "productSellingModel": {
                "id": "0jPDU0000002OTv2AM",
                "name": "One Time",
                "sellingModelType": "OneTime",
                "status": "Active"
              },
              "productSellingModelId": "0jPDU0000002OTv2AM"
            }
          ],
          "productSpecificationType": {
            "name": "Commercial",
            "productSpecificationRecordType": {}
          },
          "productType": "Bundle",
          "qualificationContext": {
            "isQualified": true
          }
        },
        {
          "additionalFields": {},
          "attributeCategories": [],
          "catalogs": [],
          "categories": [
            {
              "catalogId": "0ZSDU0000002Og64AE",
              "childCategories": [],
              "customFields": {},
              "hasSubCategories": false,
              "id": "0ZGDU0000002P0A4AU",
              "name": "Laptops",
              "qualificationContext": {
                "isQualified": true
              }
            }
          ],
          "configureDuringSale": "Allowed",
          "description": "The laptop pro bundle includes a Laptop, mouse, warranty for 2 years, premium support and printer bundle",
          "displayUrl": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCrGjPR1fvJqg4yP3RMyqjI0H9eL6tk1fvzw&amp;usqp=CAU",
          "id": "01tDU000000ExkZYAS",
          "isActive": true,
          "isAssetizable": true,
          "isSoldOnlyWithOtherProds": false,
          "name": "Laptop Pro Bundle",
          "nodeType": "bundleProduct",
          "prices": [],
          "productClassification": {},
          "productCode": "LPB001",
          "productComponentGroups": [],
          "productSellingModelOptions": [
            {
              "id": "0iODU0000002TBN2A2",
              "productId": "01tDU000000ExkZYAS",
              "productSellingModel": {
                "id": "0jPDU0000002OTv2AM",
                "name": "One Time",
                "sellingModelType": "OneTime",
                "status": "Active"
              },
              "productSellingModelId": "0jPDU0000002OTv2AM"
            }
          ],
          "productSpecificationType": {
            "name": "Commercial",
            "productSpecificationRecordType": {}
          },
          "productType": "Bundle",
          "qualificationContext": {
            "isQualified": true
          }
        },
        {
          "additionalFields": {},
          "attributeCategories": [],
          "catalogs": [],
          "categories": [
            {
              "catalogId": "0ZSDU0000002Og64AE",
              "childCategories": [],
              "customFields": {},
              "hasSubCategories": false,
              "id": "0ZGDU0000002P0A4AU",
              "name": "Laptops",
              "qualificationContext": {
                "isQualified": true
              }
            }
          ],
          "configureDuringSale": "Allowed",
          "description": "Laptop, Laptop Bag, Laptop stand, Mouse, Keyboard, USB-C Hub,External Hard Drive, Noise Cancelling Headphones, office 365",
          "displayUrl": "https://m.media-amazon.com/images/I/613Fno-NLYL._AC_SL1000_.jpg",
          "id": "01tDU000000ExlAYAS",
          "isActive": true,
          "isAssetizable": true,
          "isSoldOnlyWithOtherProds": false,
          "name": "Laptop Productivity Bundle",
          "nodeType": "bundleProduct",
          "prices": [],
          "productClassification": {},
          "productCode": "LPB001",
          "productComponentGroups": [],
          "productSellingModelOptions": [
            {
              "id": "0iODU0000002TBq2AM",
              "productId": "01tDU000000ExlAYAS",
              "productSellingModel": {
                "id": "0jPDU0000002OTv2AM",
                "name": "One Time",
                "sellingModelType": "OneTime",
                "status": "Active"
              },
              "productSellingModelId": "0jPDU0000002OTv2AM"
            }
          ],
          "productSpecificationType": {
            "name": "Commercial",
            "productSpecificationRecordType": {}
          },
          "productType": "Bundle",
          "qualificationContext": {
            "isQualified": true
          }
        }
      ],
      "total": 4
    }
    ```
:   This example shows a sample of the results of a qualification procedure that’s
    executed on a list of product IDs.
:   ```
    {
      "apiStatus": {
        "messages": [
          
        ],
        "statusCode": "FetchedDetailsSuccessfully"
      },
      "contextId": "e055bb18-d4e8-41c3-881e-0132b9561708",
      "correlationId": "c280c1b0-fd3f-4eac-9b08-075bdf1cbefc",
      "query": {
        
      },
      "result": [
        {
          "productId": "01txx0000006i7PAAQ",
          "qualificationContext": {
            "isQualified": true
          }
        },
        {
          "productId": "01txx0000006i7QAAQ",
          "qualificationContext": {
            "isQualified": true
          }
        },
        {
          "productId": "01txx0000006i7IAAQ",
          "qualificationContext": {
            "isQualified": true
          }
        }
      ]
    }
    ```
:   This example shows a list of products with eligible promotions.
:   ```
    {
      "apiStatus": {
        "messages": [],
        "statusCode": "FetchedDetailsSuccessfully"
      },
      "correlationId": "f9fb90de-36aa-44a1-9961-a9ef5fc0cad8",
      "result": {
        "catalogId": "0ZSxx0000000001GAA",
        "childCategories": [],
        "description": "Category for Samsung phones",
        "id": "0ZGxx000000004rGAA",
        "name": "Samsung",
        "isNavigational": true,
        "sortOrder": 2,
        "eligiblePromotions": [
          {
            "id": "0ZPxx0000000001AAA",
            "name": "Summer_Sale_2025",
            "displayName": "Summer Electronics Sale",
            "description": "Get 20% off on all Samsung devices",
            "priority": 100,
            "startDateTime": "2025-06-01T00:00:00Z",
            "endDateTime": "2025-08-31T23:59:59Z",
            "isAutomatic": true,
            "isCategoryPromo": true,
            "isProductPromo": false,
            "couponCode": null,
            "termsAndConditions": "Valid on all Samsung products. Cannot be combined with other offers."
          },
          {
            "id": "0ZPxx0000000002AAA",
            "name": "Electronics_Bundle",
            "displayName": "Bundle & Save",
            "description": "Save 15% when you buy 2 or more items",
            "priority": 90,
            "startDateTime": "2025-05-15T00:00:00Z",
            "endDateTime": "2025-12-31T23:59:59Z",
            "isAutomatic": false,
            "isCategoryPromo": false,
            "isProductPromo": true,
            "couponCode": "BUNDLE15",
            "termsAndConditions": "Minimum 2 items required."
          }
        ]
      }
    }
    ```
:   This example shows a sample response with visibility rule
    details.

    ```
    {
      "apiStatus": {
        "messages": [],
        "statusCode": "FetchedDetailsSuccessfully"
      },
      "contextId": "0000000r25tp21g002517756484726523db13b6a0ce245dc98062eb32a583a69",
      "correlationId": "81e072e2-e1ae-4321-9b73-d591f75854ec",
      "cursor": "MTAwMDAwMDAwNg==",
      "facets": [],
      "limit": 12,
      "query": {},
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
      "total": 1
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `api​Status` | [API Status](./connect_responses_api_status_output.htm.md "Output representation of the API status.") | Status of the API request. | Small, 60.0 | 60.0 |
| `context​Id` | String | ID of the context. | Small, 60.0 | 60.0 |
| `correlation​Id` | String | Unique ID of the request. | Small, 60.0 | 60.0 |
| `cursor` | String | Unique ID to represent the position of each product in the dataset. | Small, 60.0 | 60.0 |
| `facets` | [Search Products Facet](./connect_responses_search_products_facet.htm.md "Output representation of the details of the faceted search.") | Details of the faceted search. | Small, 63.0 | 63.0 |
| `limit` | Integer | Number of items fetched in the response. | Small, 60.0 | 60.0 |
| `offSet` | Integer | Offset size from which the item count is fetched. | Small, 60.0 | 60.0 |
| `query` | Map<String, Object> | Query that was used for the search request. | Small, 60.0 | 60.0 |
| `result` | Any response body | Result that contains the list of catalogs, categories, or products as per the requested resource. | Small, 60.0 | 60.0 |
| `total` | Integer | Number of fetched records. | Small, 60.0 | 60.0 |
| `user​Context` | [User Context](./connect_responses_user_context_output.htm.md "Output representation of the user context details.") | User context details. For example, account ID or contact ID. | Small, 60.0 | 60.0 |
