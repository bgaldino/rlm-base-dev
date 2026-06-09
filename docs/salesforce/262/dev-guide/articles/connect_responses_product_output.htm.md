---
page_id: connect_responses_product_output.htm
title: Product
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Product

Output representation of the product definition.

JSON example
:   This example shows a sample of the Product List (POST) API response.
:   ```
    {
      "products": [
          {
          "additionalFields": {
            "code__c": "SWX445"
          },
           "attributeCategory": [
            {
              "attributes": [
                {
                  "additionalFields": {
                    "scope": "Order"
                  },
                  "attributeNameOverride": "AD Text",
                  "code": "AD02",
                  "dataType": "Text",
                  "displayType": "Text",
                  "MinimumCharacterCount": "1",
                  "MaximumCharacterCount": "20",
                  "defaultValue": "AD Text DV",
                  "description": "AD Text Desc",
                  "helpText": "AD Text DHT",
                  "id": "0tjT1000000002bIAA",
                  "isHidden": false,
                  "isPriceImpacting": true,
                  "isReadOnly": true,
                  "isRequired": true,
                  "label": "AD Text Label",
                  "name": "AD Text",
                  "sequence": 1,
                  "status": "Active",
                  "valueDescription": "AD Text VD"
                }
              ],
              "code": "AC001",
              "id": "0v3T1000000000BIAQ",
              "name": "build and make"
            }
          ],
          "attributes": [
            {
              "additionalFields": {
                "scope": "SWX445"
              },
              "attributeNameOverride": "AD Picklist",
              "code": "AD001",
              "dataType": "Picklist",
              "defaultValue": "Red",
              "description": "AD Picklist Description",
              "helpText": "AD Picklist DHT",
              "id": "0tjT1000000002WIAQ",
              "isHidden": false,
              "isPriceImpacting": false,
              "isReadOnly": false,
              "isRequired": true,
              "label": "AD Picklist Label",
              "name": "AD Picklist",
              "picklist": {
                "dataType": "Text",
                "description": "APV Description",
                "id": "0v5T10000000001IAA",
                "name": "Color",
                "values": [
                  {
                    "abbreviation": "Blue Abb",
                    "code": "APV03",
                    "displayValue": "Blue DV",
                    "id": "0v6T10000000006IAA",
                    "name": "Blue",
                    "sequence": "3",
                    "value": "Blue b",
                    "status": "Active"
                  },
                  {
                    "abbreviation": "Red Abb",
                    "code": "APV04",
                    "displayValue": "Red",
                    "id": "0v6T10000000001IAA",
                    "name": "Red",
                    "sequence": "4",
                    "value": "Red",
                    "status": "Active"
                  },
                  {
                    "abbreviation": "One Abb",
                    "code": "APV02",
                    "displayValue": "One DV",
                    "id": "0v6T1000000000uIAA",
                    "name": "One",
                    "sequence": "2",
                    "value": "One 1",
                    "status": "Active"
                  },
                  {
                    "abbreviation": "Red Abbreviation",
                    "code": "APV01",
                    "displayValue": "Red Display Value",
                    "id": "0v6T1000000001OIAQ",
                    "name": "Red",
                    "sequence": "1",
                    "value": "red12",
                    "status": "Active"
                  }
                ]
              },
              "sequence": 1,
              "status": "Active",
              "valueDescription": "AD Picklist VD"
            }
          ],
          "categories": [],
          "childProducts": [
            {
              "attributeCategory": [],
              "attributes": [],
              "categories": [],
              "childProducts": [],
              "configureDuringSale": "NotAllowed",
              "id": "01tZ7000000AJkaIAG",
              "isActive": false,
              "isAssetizable": true,
              "isSoldOnlyWithOtherProds": false,
              "name": "Earphones",
              "nodeType": "bundleProduct",
              "productComponentGroups": [],
              "productRelatedComponent": {
                "childProductId": "01tZ7000000AJkaIAG",
                "doesBundlePriceIncludeChild": true,
                "id": "0dSZ700000000cdMAA",
                "isComponentRequired": false,
                "isDefaultComponent": true,
                "isExcluded": false,
                "isQuantityEditable": false,
                "parentProductId": "01tZ7000000AJXOIA4",
                "productRelationshipTypeId": "0yoZ700000000kPIAQ",
                "quantity": 1,
                "quantityScaleMethod": "Proportional"
              },
              "productSellingModelOptions": []
            }
          ],
          "description": "Keep your organization connected with seamless collaboration across distributed teams. No matter where employees are located, organizations are seeking stronger employee engagement and customer experiences to enable more productivity and greater business agility. More effective collaboration helps organizations work smarter.",
          "displayUrl": "https://dispatch.m.io/wp-content/uploads/2023/01/History-of-Webex.png",
          "id": "01t1Q000008CD2eQAG",
          "isActive": true,
          "isAssetizable": true,
          "isSoldOnlyWithOtherProds": false,
          "name": "SmartBytes Collaboration Suite",
          "nodeType": "bundleProduct",
          "productClassification": {
            "id": "11B1Q0000008OMGUA2"
          },
          "productCode": "P0143",
          "productComponentGroups": [
            {
              "components": [
                {
                  "attributeCategory": [],
                  "attributes": [],
                  "categories": [],
                  "childProducts": [],
                  "id": "01tZ7000000AJXTIA4",
                  "isActive": false,
                  "isAssetizable": true,
                  "isSoldOnlyWithOtherProds": false,
                  "name": "Charger",
                  "nodeType": "bundleProduct",
                  "productComponentGroups": [],
                  "productRelatedComponent": {
                    "childProductId": "01tZ7000000AJXTIA4",
                    "doesBundlePriceIncludeChild": true,
                    "id": "0dSZ700000000YLMAY",
                    "isComponentRequired": false,
                    "isDefaultComponent": true,
                    "isExcluded": false,
                    "isQuantityEditable": false,
                    "parentProductId": "01tZ7000000AJXOIA4",
                    "productRelationshipTypeId": "0yoZ700000000kPIAQ",
                    "quantity": 1,
                    "quantityScaleMethod": "Proportional"
                  },
                  "productSellingModelOptions": []
                }
              ],
              "id": "0y7Z700000000TtIAI",
              "isExcluded": false,
              "name": "Box",
              "parentProductId": "01tZ7000000AJXOIA4"
            }
          ],
          "productSellingModelOptions": [
            {
              "id": "0iO1Q0000008OkeUAE",
              "productId": "01t1Q000008CD2eQAG",
              "productSellingModel": {
                "id": "0jP1Q000000CaVFUA0",
                "isDefault": true,
                "name": "One Time",
                "sellingModelType": "OneTime",
                "status": "Active"
              }
            }
          ],
          "productSpecificationType": {
            "name": "None"
          }
        }
    ],
      "status": {
        "code": "200",
        "correlationId": "fd158d80-d73c-4a1f-a009-9225db804d70",
        "errors": [],
        "message": "Successfully fetched product records."
      }
    }
    ```
:   This example shows a sample of the Bulk Product Details (POST) API response.
:   ```
    {
      "products": [
          {
          "additionalFields": {
            "code__c": "SWX445"
          },
           "attributeCategory": [
            {
              "attributes": [
                {
                  "additionalFields": {
                    "scope": "Order"
                  },
                  "attributeNameOverride": "AD Text",
                  "code": "AD02",
                  "dataType": "Text",
                  "displayType": "Text",
                  "MinimumCharacterCount": "1",
                  "MaximumCharacterCount": "20",
                  "defaultValue": "AD Text DV",
                  "description": "AD Text Desc",
                  "helpText": "AD Text DHT",
                  "id": "0tjT1000000002bIAA",
                  "isHidden": false,
                  "isPriceImpacting": true,
                  "isReadOnly": true,
                  "isRequired": true,
                  "label": "AD Text Label",
                  "name": "AD Text",
                  "sequence": 1,
                  "status": "Active",
                  "valueDescription": "AD Text VD"
                }
              ],
              "code": "AC001",
              "id": "0v3T1000000000BIAQ",
              "name": "build and make"
            }
          ],
          "attributes": [
            {
              "additionalFields": {
                "scope": "SWX445"
              },
              "attributeNameOverride": "AD Picklist",
              "code": "AD001",
              "dataType": "Picklist",
              "defaultValue": "Red",
              "description": "AD Picklist Description",
              "helpText": "AD Picklist DHT",
              "id": "0tjT1000000002WIAQ",
              "isHidden": false,
              "isPriceImpacting": false,
              "isReadOnly": false,
              "isRequired": true,
              "label": "AD Picklist Label",
              "name": "AD Picklist",
              "picklist": {
                "dataType": "Text",
                "description": "APV Description",
                "id": "0v5T10000000001IAA",
                "name": "Color",
                "values": [
                  {
                    "abbreviation": "Blue Abb",
                    "code": "APV03",
                    "displayValue": "Blue DV",
                    "id": "0v6T10000000006IAA",
                    "name": "Blue",
                    "sequence": "3",
                    "value": "Blue b",
                    "status": "Active"
                  },
                  {
                    "abbreviation": "Red Abb",
                    "code": "APV04",
                    "displayValue": "Red",
                    "id": "0v6T10000000001IAA",
                    "name": "Red",
                    "sequence": "4",
                    "value": "Red",
                    "status": "Active"
                  },
                  {
                    "abbreviation": "One Abb",
                    "code": "APV02",
                    "displayValue": "One DV",
                    "id": "0v6T1000000000uIAA",
                    "name": "One",
                    "sequence": "2",
                    "value": "One 1",
                    "status": "Active"
                  },
                  {
                    "abbreviation": "Red Abbreviation",
                    "code": "APV01",
                    "displayValue": "Red Display Value",
                    "id": "0v6T1000000001OIAQ",
                    "name": "Red",
                    "sequence": "1",
                    "value": "red12",
                    "status": "Active"
                  }
                ]
              },
              "sequence": 1,
              "status": "Active",
              "valueDescription": "AD Picklist VD"
            }
          ],
          "categories": [],
          "childProducts": [
            {
              "attributeCategory": [],
              "attributes": [],
              "categories": [],
              "childProducts": [],
              "configureDuringSale": "NotAllowed",
              "id": "01tZ7000000AJkaIAG",
              "isActive": false,
              "isAssetizable": true,
              "isSoldOnlyWithOtherProds": false,
              "name": "Earphones",
              "nodeType": "bundleProduct",
              "productComponentGroups": [],
              "productRelatedComponent": {
                "childProductId": "01tZ7000000AJkaIAG",
                "doesBundlePriceIncludeChild": true,
                "id": "0dSZ700000000cdMAA",
                "isComponentRequired": false,
                "isDefaultComponent": true,
                "isExcluded": false,
                "isQuantityEditable": false,
                "parentProductId": "01tZ7000000AJXOIA4",
                "productRelationshipTypeId": "0yoZ700000000kPIAQ",
                "quantity": 1,
                "quantityScaleMethod": "Proportional"
              },
              "productSellingModelOptions": []
            }
          ],
          "description": "Keep your organization connected with seamless collaboration across distributed teams. No matter where employees are located, organizations are seeking stronger employee engagement and customer experiences to enable more productivity and greater business agility. More effective collaboration helps organizations work smarter.",
          "displayUrl": "https://dispatch.m.io/wp-content/uploads/2023/01/History-of-Webex.png",
          "id": "01t1Q000008CD2eQAG",
          "isActive": true,
          "isAssetizable": true,
          "isSoldOnlyWithOtherProds": false,
          "name": "SmartBytes Collaboration Suite",
          "nodeType": "bundleProduct",
          "productClassification": {
            "id": "11B1Q0000008OMGUA2",
            "name" : "class",
            "code" : "code",
            "status" : "Active"
          },
          "productCode": "P0143",
          "productComponentGroups": [
            {
              "components": [
                {
                  "attributeCategory": [],
                  "attributes": [],
                  "categories": [],
                  "childProducts": [],
                  "id": "01tZ7000000AJXTIA4",
                  "isActive": false,
                  "isAssetizable": true,
                  "isSoldOnlyWithOtherProds": false,
                  "name": "Charger",
                  "nodeType": "bundleProduct",
                  "productComponentGroups": [],
                  "productRelatedComponent": {
                    "childProductId": "01tZ7000000AJXTIA4",
                    "doesBundlePriceIncludeChild": true,
                    "id": "0dSZ700000000YLMAY",
                    "isComponentRequired": false,
                    "isDefaultComponent": true,
                    "isExcluded": false,
                    "isQuantityEditable": false,
                    "parentProductId": "01tZ7000000AJXOIA4",
                    "productRelationshipTypeId": "0yoZ700000000kPIAQ",
                    "quantity": 1,
                    "quantityScaleMethod": "Proportional"
                  },
                  "productSellingModelOptions": []
                }
              ],
              "id": "0y7Z700000000TtIAI",
              "isExcluded": false,
              "name": "Box",
              "parentProductId": "01tZ7000000AJXOIA4"
            }
          ],
          "productSellingModelOptions": [
            {
              "id": "0iO1Q0000008OkeUAE",
              "productId": "01t1Q000008CD2eQAG",
              "productSellingModel": {
                "id": "0jP1Q000000CaVFUA0",
                "isDefault": true,
                "name": "One Time",
                "sellingModelType": "OneTime",
                "status": "Active"
              }
            }
          ],
          "productSpecificationType": {
            "name": "None"
          }
        }
    ],
      "status": {
        "code": "200",
        "correlationId": "fd158d80-d73c-4a1f-a009-9225db804d70",
        "errors": [],
        "message": "Successfully fetched product records."
      }
    }
    ```
:   This example shows a sample of the Product By ID (GET) API response.
:   ```
    {
      "products": [
        {
          "attributeCategory": [
            {
              "attributes": [
                {
                  "attributeNameOverride": "AD Text",
                  "code": "AD02",
                  "dataType": "Text",
                  "displayType": "Text",
                  "MinimumCharacterCount": "1",
                  "MaximumCharacterCount": "20",
                  "defaultValue": "AD Text DV",
                  "description": "AD Text Desc",
                  "helpText": "AD Text DHT",
                  "id": "0tjT1000000002bIAA",
                  "isHidden": false,
                  "isPriceImpacting": true,
                  "isReadOnly": true,
                  "isRequired": true,
                  "label": "AD Text Label",
                  "name": "AD Text",
                  "sequence": 1,
                  "status": "Active",
                  "valueDescription": "AD Text VD"
                }
              ],
              "code": "AC001",
              "id": "0v3T1000000000BIAQ",
              "name": "build and make"
            }
          ],
          "attributes": [
            {
              "attributeNameOverride": "AD Picklist",
              "code": "AD001",
              "dataType": "Picklist",
              "defaultValue": "Red",
              "description": "AD Picklist Description",
              "helpText": "AD Picklist DHT",
              "id": "0tjT1000000002WIAQ",
              "isHidden": false,
              "isPriceImpacting": false,
              "isReadOnly": false,
              "isRequired": true,
              "label": "AD Picklist Label",
              "name": "AD Picklist",
              "picklist": {
                "dataType": "Text",
                "description": "APV Description",
                "id": "0v5T10000000001IAA",
                "name": "Color",
                "values": [
                  {
                    "abbreviation": "Blue Abb",
                    "code": "APV03",
                    "displayValue": "Blue DV",
                    "id": "0v6T10000000006IAA",
                    "name": "Blue",
                    "sequence": "3",
                    "value": "Blue b",
                    "status": "Active"
                  },
                  {
                    "abbreviation": "Red Abb",
                    "code": "APV04",
                    "displayValue": "Red",
                    "id": "0v6T10000000001IAA",
                    "name": "Red",
                    "sequence": "4",
                    "value": "Red",
                    "status": "Active"
                  },
                  {
                    "abbreviation": "One Abb",
                    "code": "APV02",
                    "displayValue": "One DV",
                    "id": "0v6T1000000000uIAA",
                    "name": "One",
                    "sequence": "2",
                    "value": "One 1",
                    "status": "Active"
                  },
                  {
                    "abbreviation": "Red Abbreviation",
                    "code": "APV01",
                    "displayValue": "Red Display Value",
                    "id": "0v6T1000000001OIAQ",
                    "name": "Red",
                    "sequence": "1",
                    "value": "red12",
                    "status": "Active"
                  }
                ]
              },
              "sequence": 1,
              "status": "Active",
              "valueDescription": "AD Picklist VD"
            }
          ],
          "availabilityDate": "2023-07-12T19:00:00.000Z",
          "categories": [],
          "childProducts": [],
          "configureDuringSale": "Allowed",
          "description": "Bundle Product Description",
          "discontinuedDate": "2023-07-27T19:00:00.000Z",
          "displayUrl": "www.google.com",
          "endOfLifeDate": "2023-07-31T19:00:00.000Z",
          "id": "01tT1000000F0afIAC",
          "isActive": true,
          "isAssetizable": true,
          "isSoldOnlyWithOtherProds": true,
          "name": "Bundle Product",
          "nodeType": "bundleProduct",
          "productClassification": {
            "id": "11BT10000004C9SMAU",
            "name" : "class",
            "code" : "code",
            "status" : "Active"
          },
          "productCode": "P001",
          "productComponentGroups": [
            {
              "code": "PCG002",
              "components": [
                {
                  "attributeCategory": [],
                  "attributes": [],
                  "categories": [],
                  "childProducts": [],
                  "nodeType": "productClass",
                  "productClassification": {
                    "id": "11BT10000004C9SMAU",
                    "name" : "class",
                    "code" : "code",
                    "status" : "Active"
                  },
                  "productComponentGroups": [],
                  "productRelatedComponent": {
                    "childSellingModelId": "0jPT10000004CAfMAM",
                    "doesBundlePriceIncludeChild": true,
                    "id": "0dST100000000rlMAA",
                    "isComponentRequired": false,
                    "isDefaultComponent": false,
                    "isQuantityEditable": true,
                    "maxQuantity": 5,
                    "minQuantity": 1,
                    "parentProductId": "01tT1000000F0afIAC",
                    "productClassificationId": "11BT10000004C9SMAU",
                    "productRelationshipTypeId": "0yoT10000004CBEIA2",
                    "quantity": 1,
                    "quantityScaleMethod": "Proportional",
                    "sequence": 2,
                    "isExcluded": false
                  },
                  "productSellingModelOptions": []
                }
              ],
              "description": "PCG002 desc",
              "id": "0y7T10000004C9IIAU",
              "maxBundleComponents": 5,
              "minBundleComponents": 1,
              "name": "PCG002",
              "parentProductId": "01tT1000000F0afIAC",
              "sequence": 2,
              "isExcluded": false
            },
            {
              "code": "PCG001",
              "components": [
                {
                  "attributeCategory": [],
                  "attributes": [
                    {
                      "attributeNameOverride": "AD Picklist",
                      "code": "AD001",
                      "dataType": "Picklist",
                      "defaultValue": "Red",
                      "description": "AD Picklist Description",
                      "helpText": "AD Picklist DHT",
                      "id": "0tjT1000000002WIAQ",
                      "isHidden": false,
                      "isPriceImpacting": false,
                      "isReadOnly": false,
                      "isRequired": true,
                      "label": "AD Picklist Label",
                      "name": "AD Picklist",
                      "picklist": {
                        "dataType": "Text",
                        "description": "APV Description",
                        "id": "0v5T10000000001IAA",
                        "name": "Color",
                        "values": [
                          {
                            "abbreviation": "Blue Abb",
                            "code": "APV03",
                            "displayValue": "Blue DV",
                            "id": "0v6T10000000006IAA",
                            "name": "Blue",
                            "sequence": "3",
                            "value": "Blue b",
                            "status": "Active"
                          },
                          {
                            "abbreviation": "Red Abb",
                            "code": "APV04",
                            "displayValue": "Red",
                            "id": "0v6T10000000001IAA",
                            "name": "Red",
                            "sequence": "4",
                            "value": "Red",
                            "status": "Active"
                          },
                          {
                            "abbreviation": "One Abb",
                            "code": "APV02",
                            "displayValue": "One DV",
                            "id": "0v6T1000000000uIAA",
                            "name": "One",
                            "sequence": "2",
                            "value": "One 1",
                            "status": "Active"
                          },
                          {
                            "abbreviation": "Red Abbreviation",
                            "code": "APV01",
                            "displayValue": "Red Display Value",
                            "id": "0v6T1000000001OIAQ",
                            "name": "Red",
                            "sequence": "1",
                            "value": "red12",
                            "status": "Active"
                          }
                        ]
                      },
                      "sequence": 1,
                      "status": "Active",
                      "valueDescription": "AD Picklist VD"
                    },
                    {
                      "attributeNameOverride": "AD Text",
                      "code": "AD02",
                      "dataType": "Text",
                      "displayType": "Text",
                      "MinimumCharacterCount": "1",
                      "MaximumCharacterCount": "20",
                      "defaultValue": "AD Text DV",
                      "description": "AD Text Desc",
                      "helpText": "AD Text DHT",
                      "id": "0tjT1000000002bIAA",
                      "isHidden": false,
                      "isPriceImpacting": false,
                      "isReadOnly": false,
                      "isRequired": true,
                      "label": "AD Text Label",
                      "name": "AD Text",
                      "status": "Active",
                      "valueDescription": "AD Text VD"
                    }
                  ],
                  "availabilityDate": "2023-07-17T19:00:00.000Z",
                  "categories": [],
                  "childProducts": [],
                  "configureDuringSale": "Allowed",
                  "description": "P003 desc",
                  "discontinuedDate": "2023-07-19T19:00:00.000Z",
                  "displayUrl": "www.google.com",
                  "endOfLifeDate": "2023-07-28T19:00:00.000Z",
                  "id": "01tT1000000F0YyIAK",
                  "isActive": false,
                  "isAssetizable": true,
                  "isSoldOnlyWithOtherProds": false,
                  "name": "Child1 - Bundle with PCG",
                  "nodeType": "bundleProduct",
                  "productClassification": {
                    "id": "11BT10000004C9SMAU",
                    "name" : "class",
                    "code" : "code",
                    "status" : "Active"
                  },
                  "productCode": "P003",
                  "productComponentGroups": [
                    {
                      "code": "PCG2",
                      "components": [
                        {
                          "attributeCategory": [],
                          "attributes": [],
                          "categories": [],
                          "childProducts": [],
                          "id": "01tT1000000F0Z8IAK",
                          "isActive": false,
                          "isAssetizable": true,
                          "isSoldOnlyWithOtherProds": false,
                          "name": "Super Child2 - Bundle with PCG",
                          "nodeType": "bundleProduct",
                          "productComponentGroups": [],
                          "productRelatedComponent": {
                            "childProductId": "01tT1000000F0Z8IAK",
                            "doesBundlePriceIncludeChild": true,
                            "id": "0dST100000000rWMAQ",
                            "isComponentRequired": false,
                            "isDefaultComponent": false,
                            "isQuantityEditable": false,
                            "parentProductId": "01tT1000000F0YyIAK",
                            "productRelationshipTypeId": "0yoT1000000002WIAQ",
                            "quantity": 1,
                            "quantityScaleMethod": "Proportional",
                            "sequence": 2,
                            "isExcluded": false
                          },
                          "productSellingModelOptions": [],
                          "productSpecificationType": {
                            "name": "NonCommercialSpecType",
                            "productSpecificationRecordType": null
                          }
                        },
                        {
                          "attributeCategory": [],
                          "attributes": [],
                          "availabilityDate": "2023-07-15T19:00:00.000Z",
                          "categories": [],
                          "childProducts": [],
                          "configureDuringSale": "Allowed",
                          "discontinuedDate": "2023-07-16T19:00:00.000Z",
                          "displayUrl": "Test",
                          "endOfLifeDate": "2023-07-17T19:00:00.000Z",
                          "id": "01tT1000000F0YzIAK",
                          "isActive": false,
                          "isAssetizable": true,
                          "isSoldOnlyWithOtherProds": false,
                          "name": "SuperChild1 - Bundle with PCG",
                          "nodeType": "bundleProduct",
                          "productCode": "Test",
                          "productComponentGroups": [],
                          "productRelatedComponent": {
                            "childProductId": "01tT1000000F0YzIAK",
                            "doesBundlePriceIncludeChild": true,
                            "id": "0dST100000000rXMAQ",
                            "isComponentRequired": false,
                            "isDefaultComponent": false,
                            "isQuantityEditable": false,
                            "parentProductId": "01tT1000000F0YyIAK",
                            "productRelationshipTypeId": "0yoT1000000002WIAQ",
                            "quantity": 1,
                            "quantityScaleMethod": "Proportional",
                            "sequence": 1,
                            "isExcluded": false
                          },
                          "productSellingModelOptions": [],
                          "productSpecificationType": {
                            "name": "NonCommercialSpecType",
                            "productSpecificationRecordType": null
                          }
                        },
                        {
                          "attributeCategory": [],
                          "attributes": [],
                          "categories": [],
                          "childProducts": [],
                          "configureDuringSale": "Allowed",
                          "id": "01tT1000000F0apIAC",
                          "isActive": false,
                          "isAssetizable": true,
                          "isSoldOnlyWithOtherProds": false,
                          "name": "Bundle2",
                          "nodeType": "bundleProduct",
                          "productCode": "PC003",
                          "productComponentGroups": [],
                          "productRelatedComponent": {
                            "childProductId": "01tT1000000F0apIAC",
                            "doesBundlePriceIncludeChild": true,
                            "id": "0dST100000000rqMAA",
                            "isComponentRequired": false,
                            "isDefaultComponent": false,
                            "isQuantityEditable": false,
                            "parentProductId": "01tT1000000F0YyIAK",
                            "productRelationshipTypeId": "0yoT1000000002WIAQ",
                            "quantity": 1,
                            "quantityScaleMethod": "Proportional",
                            "isExcluded": false
                          },
                          "productSellingModelOptions": [],
                          "productSpecificationType": {
                            "name": "NonCommercialSpecType",
                            "productSpecificationRecordType": null
                          }
                        }
                      ],
                      "description": "Group for components at level 2",
                      "id": "0y7T10000004C98IAE",
                      "maxBundleComponents": 5,
                      "minBundleComponents": 1,
                      "name": "PCG2",
                      "parentProductId": "01tT1000000F0YyIAK",
                      "isExcluded": false
                    }
                  ],
                  "productRelatedComponent": {
                    "childProductId": "01tT1000000F0YyIAK",
                    "childSellingModelId": "0jPT10000004CAfMAM",
                    "doesBundlePriceIncludeChild": true,
                    "id": "0dST100000000rgMAA",
                    "isComponentRequired": false,
                    "isDefaultComponent": false,
                    "isQuantityEditable": true,
                    "maxQuantity": 3,
                    "minQuantity": 1,
                    "parentProductId": "01tT1000000F0afIAC",
                    "parentSellingModelId": "0jPT10000004CAfMAM",
                    "productRelationshipTypeId": "0yoT1000000002WIAQ",
                    "quantity": 1,
                    "quantityScaleMethod": "Proportional",
                    "sequence": 1,
                    "isExcluded": false
                  },
                  "productSellingModelOptions": [
                    {
                      "id": "0iOT10000004CMrMAM",
                      "productId": "01tT1000000F0YyIAK",
                      "isDefault": false,
                      "productSellingModel": {
                        "id": "0jPT10000004CAfMAM",
                        "name": "OneTimePSM",
                        "sellingModelType": "OneTime",
                        "status": "Active"
                      }
                    }
                  ],
                  "productSpecificationType": {
                    "name": "NonCommercialSpecType",
                    "productSpecificationRecordType": null
                  }
                }
              ],
              "description": "PCG001 Description",
              "id": "0y7T10000004C9DIAU",
              "maxBundleComponents": 5,
              "minBundleComponents": 1,
              "name": "PCG001",
              "parentProductId": "01tT1000000F0afIAC",
              "sequence": 1,
              "isExcluded": false
            }
          ],
          "productSellingModelOptions": [
            {
              "id": "0iOT10000004CMmMAM",
              "productId": "01tT1000000F0afIAC",
              "productSellingModel": {
                "id": "0jPT10000004CAfMAM",
                "name": "OneTimePSM",
                "sellingModelType": "OneTime",
                "status": "Active"
              }
            }
          ],
          "productSpecificationType": {
            "name": "NonCommercialSpecType",
            "productSpecificationRecordType": null
          }
        },
        {
          "attributeCategory": [
            {
              "attributes": [
                {
                  "attributeNameOverride": "AD Text",
                  "code": "AD02",
                  "dataType": "Text",
                  "displayType": "Text",
                  "MinimumCharacterCount": "1",
                  "MaximumCharacterCount": "20",
                  "defaultValue": "AD Text DV",
                  "description": "AD Text Desc",
                  "helpText": "AD Text DHT",
                  "id": "0tjT1000000002bIAA",
                  "isHidden": false,
                  "isPriceImpacting": true,
                  "isReadOnly": true,
                  "isRequired": true,
                  "label": "AD Text Label",
                  "name": "AD Text",
                  "sequence": 1,
                  "status": "Active",
                  "valueDescription": "AD Text VD"
                }
              ],
              "code": "AC001",
              "id": "0v3T1000000000BIAQ",
              "name": "build and make"
            }
          ],
          "attributes": [
            {
              "attributeNameOverride": "AD Picklist",
              "code": "AD001",
              "dataType": "Picklist",
              "defaultValue": "Red",
              "description": "AD Picklist Description",
              "helpText": "AD Picklist DHT",
              "id": "0tjT1000000002WIAQ",
              "isHidden": false,
              "isPriceImpacting": false,
              "isReadOnly": false,
              "isRequired": true,
              "label": "AD Picklist Label",
              "name": "AD Picklist",
              "picklist": {
                "dataType": "Text",
                "description": "APV Description",
                "id": "0v5T10000000001IAA",
                "name": "Color",
                "values": [
                  {
                    "abbreviation": "Blue Abb",
                    "code": "APV03",
                    "displayValue": "Blue DV",
                    "id": "0v6T10000000006IAA",
                    "name": "Blue",
                    "sequence": "3",
                    "value": "Blue b",
                    "status": "Active"
                  },
                  {
                    "abbreviation": "Red Abb",
                    "code": "APV04",
                    "displayValue": "Red",
                    "id": "0v6T10000000001IAA",
                    "name": "Red",
                    "sequence": "4",
                    "value": "Red",
                    "status": "Active"
                  },
                  {
                    "abbreviation": "One Abb",
                    "code": "APV02",
                    "displayValue": "One DV",
                    "id": "0v6T1000000000uIAA",
                    "name": "One",
                    "sequence": "2",
                    "value": "One 1",
                    "status": "Active"
                  },
                  {
                    "abbreviation": "Red Abbreviation",
                    "code": "APV01",
                    "displayValue": "Red Display Value",
                    "id": "0v6T1000000001OIAQ",
                    "name": "Red",
                    "sequence": "1",
                    "value": "red12",
                    "status": "Active"
                  }
                ]
              },
              "sequence": 1,
              "status": "Active",
              "valueDescription": "AD Picklist VD"
            }
          ],
          "availabilityDate": "2023-07-12T19:00:00.000Z",
          "categories": [],
          "childProducts": [],
          "configureDuringSale": "Allowed",
          "description": "Bundle Product Description",
          "discontinuedDate": "2023-07-27T19:00:00.000Z",
          "displayUrl": "www.google.com",
          "endOfLifeDate": "2023-07-31T19:00:00.000Z",
          "id": "01tT1000000F0afIAC",
          "isActive": true,
          "isAssetizable": true,
          "isSoldOnlyWithOtherProds": true,
          "name": "Bundle Product",
          "nodeType": "bundleProduct",
          "productClassification": {
            "id": "11BT10000004C9SMAU",
            "name" : "class",
            "code" : "code",
            "status" : "Active"
          },
          "productCode": "P001",
          "productComponentGroups": [
            {
              "code": "PCG002",
              "components": [
                {
                  "attributeCategory": [],
                  "attributes": [],
                  "categories": [],
                  "childProducts": [],
                  "nodeType": "productClass",
                  "productClassification": {
                    "id": "11BT10000004C9SMAU",
                    "name" : "class",
                    "code" : "code",
                    "status" : "Active"
                  },
                  "productComponentGroups": [],
                  "productRelatedComponent": {
                    "childSellingModelId": "0jPT10000004CAfMAM",
                    "doesBundlePriceIncludeChild": true,
                    "id": "0dST100000000rlMAA",
                    "isComponentRequired": false,
                    "isDefaultComponent": false,
                    "isQuantityEditable": true,
                    "maxQuantity": 5,
                    "minQuantity": 1,
                    "parentProductId": "01tT1000000F0afIAC",
                    "productClassificationId": "11BT10000004C9SMAU",
                    "productRelationshipTypeId": "0yoT10000004CBEIA2",
                    "quantity": 1,
                    "quantityScaleMethod": "Proportional",
                    "sequence": 2,
                    "isExcluded": false
                  },
                  "productSellingModelOptions": []
                }
              ],
              "description": "PCG002 desc",
              "id": "0y7T10000004C9IIAU",
              "maxBundleComponents": 5,
              "minBundleComponents": 1,
              "name": "PCG002",
              "parentProductId": "01tT1000000F0afIAC",
              "sequence": 2,
              "isExcluded": false
            },
            {
              "code": "PCG001",
              "components": [
                {
                  "attributeCategory": [],
                  "attributes": [
                    {
                      "attributeNameOverride": "AD Picklist",
                      "code": "AD001",
                      "dataType": "Picklist",
                      "defaultValue": "Red",
                      "description": "AD Picklist Description",
                      "helpText": "AD Picklist DHT",
                      "id": "0tjT1000000002WIAQ",
                      "isHidden": false,
                      "isPriceImpacting": false,
                      "isReadOnly": false,
                      "isRequired": true,
                      "label": "AD Picklist Label",
                      "name": "AD Picklist",
                      "picklist": {
                        "dataType": "Text",
                        "description": "APV Description",
                        "id": "0v5T10000000001IAA",
                        "name": "Color",
                        "values": [
                          {
                            "abbreviation": "Blue Abb",
                            "code": "APV03",
                            "displayValue": "Blue DV",
                            "id": "0v6T10000000006IAA",
                            "name": "Blue",
                            "sequence": "3",
                            "value": "Blue b",
                            "status": "Active"
                          },
                          {
                            "abbreviation": "Red Abb",
                            "code": "APV04",
                            "displayValue": "Red",
                            "id": "0v6T10000000001IAA",
                            "name": "Red",
                            "sequence": "4",
                            "value": "Red",
                            "status": "Active"
                          },
                          {
                            "abbreviation": "One Abb",
                            "code": "APV02",
                            "displayValue": "One DV",
                            "id": "0v6T1000000000uIAA",
                            "name": "One",
                            "sequence": "2",
                            "value": "One 1",
                            "status": "Active"
                          },
                          {
                            "abbreviation": "Red Abbreviation",
                            "code": "APV01",
                            "displayValue": "Red Display Value",
                            "id": "0v6T1000000001OIAQ",
                            "name": "Red",
                            "sequence": "1",
                            "value": "red12",
                            "status": "Active"
                          }
                        ]
                      },
                      "sequence": 1,
                      "status": "Active",
                      "valueDescription": "AD Picklist VD"
                    },
                    {
                      "attributeNameOverride": "AD Text",
                      "code": "AD02",
                      "dataType": "Text",
                      "displayType": "Text",
                      "MinimumCharacterCount": "1",
                      "MaximumCharacterCount": "20",
                      "defaultValue": "AD Text DV",
                      "description": "AD Text Desc",
                      "helpText": "AD Text DHT",
                      "id": "0tjT1000000002bIAA",
                      "isHidden": false,
                      "isPriceImpacting": false,
                      "isReadOnly": false,
                      "isRequired": true,
                      "label": "AD Text Label",
                      "name": "AD Text",
                      "status": "Active",
                      "valueDescription": "AD Text VD"
                    }
                  ],
                  "availabilityDate": "2023-07-17T19:00:00.000Z",
                  "categories": [],
                  "childProducts": [],
                  "configureDuringSale": "Allowed",
                  "description": "P003 desc",
                  "discontinuedDate": "2023-07-19T19:00:00.000Z",
                  "displayUrl": "www.google.com",
                  "endOfLifeDate": "2023-07-28T19:00:00.000Z",
                  "id": "01tT1000000F0YyIAK",
                  "isActive": false,
                  "isAssetizable": true,
                  "isSoldOnlyWithOtherProds": false,
                  "name": "Child1 - Bundle with PCG",
                  "nodeType": "bundleProduct",
                  "productClassification": {
                    "id": "11BT10000004C9SMAU",
                    "name" : "class",
                    "code" : "code",
                    "status" : "Active"
                  },
                  "productCode": "P003",
                  "productComponentGroups": [
                    {
                      "code": "PCG2",
                      "components": [
                        {
                          "attributeCategory": [],
                          "attributes": [],
                          "categories": [],
                          "childProducts": [],
                          "id": "01tT1000000F0Z8IAK",
                          "isActive": false,
                          "isAssetizable": true,
                          "isSoldOnlyWithOtherProds": false,
                          "name": "Super Child2 - Bundle with PCG",
                          "nodeType": "bundleProduct",
                          "productComponentGroups": [],
                          "productRelatedComponent": {
                            "childProductId": "01tT1000000F0Z8IAK",
                            "doesBundlePriceIncludeChild": true,
                            "id": "0dST100000000rWMAQ",
                            "isComponentRequired": false,
                            "isDefaultComponent": false,
                            "isQuantityEditable": false,
                            "parentProductId": "01tT1000000F0YyIAK",
                            "productRelationshipTypeId": "0yoT1000000002WIAQ",
                            "quantity": 1,
                            "quantityScaleMethod": "Proportional",
                            "sequence": 2,
                            "isExcluded": false
                          },
                          "productSellingModelOptions": [],
                          "productSpecificationType": {
                            "name": "NonCommercialSpecType",
                            "productSpecificationRecordType": null
                          }
                        },
                        {
                          "attributeCategory": [],
                          "attributes": [],
                          "availabilityDate": "2023-07-15T19:00:00.000Z",
                          "categories": [],
                          "childProducts": [],
                          "configureDuringSale": "Allowed",
                          "discontinuedDate": "2023-07-16T19:00:00.000Z",
                          "displayUrl": "Test",
                          "endOfLifeDate": "2023-07-17T19:00:00.000Z",
                          "id": "01tT1000000F0YzIAK",
                          "isActive": false,
                          "isAssetizable": true,
                          "isSoldOnlyWithOtherProds": false,
                          "name": "SuperChild1 - Bundle with PCG",
                          "nodeType": "bundleProduct",
                          "productCode": "Test",
                          "productComponentGroups": [],
                          "productRelatedComponent": {
                            "childProductId": "01tT1000000F0YzIAK",
                            "doesBundlePriceIncludeChild": true,
                            "id": "0dST100000000rXMAQ",
                            "isComponentRequired": false,
                            "isDefaultComponent": false,
                            "isQuantityEditable": false,
                            "parentProductId": "01tT1000000F0YyIAK",
                            "productRelationshipTypeId": "0yoT1000000002WIAQ",
                            "quantity": 1,
                            "quantityScaleMethod": "Proportional",
                            "sequence": 1,
                            "isExcluded": false
                          },
                          "productSellingModelOptions": [],
                          "productSpecificationType": {
                            "name": "NonCommercialSpecType",
                            "productSpecificationRecordType": null
                          }
                        },
                        {
                          "attributeCategory": [],
                          "attributes": [],
                          "categories": [],
                          "childProducts": [],
                          "configureDuringSale": "Allowed",
                          "id": "01tT1000000F0apIAC",
                          "isActive": false,
                          "isAssetizable": true,
                          "isSoldOnlyWithOtherProds": false,
                          "name": "Bundle2",
                          "nodeType": "bundleProduct",
                          "productCode": "PC003",
                          "productComponentGroups": [],
                          "productRelatedComponent": {
                            "childProductId": "01tT1000000F0apIAC",
                            "doesBundlePriceIncludeChild": true,
                            "id": "0dST100000000rqMAA",
                            "isComponentRequired": false,
                            "isDefaultComponent": false,
                            "isQuantityEditable": false,
                            "parentProductId": "01tT1000000F0YyIAK",
                            "productRelationshipTypeId": "0yoT1000000002WIAQ",
                            "quantity": 1,
                            "quantityScaleMethod": "Proportional",
                            "isExcluded": false
                          },
                          "productSellingModelOptions": [],
                          "productSpecificationType": {
                            "name": "NonCommercialSpecType",
                            "productSpecificationRecordType": null
                          }
                        }
                      ],
                      "description": "Group for components at level 2",
                      "id": "0y7T10000004C98IAE",
                      "maxBundleComponents": 5,
                      "minBundleComponents": 1,
                      "name": "PCG2",
                      "parentProductId": "01tT1000000F0YyIAK",
                      "isExcluded": false
                    }
                  ],
                  "productRelatedComponent": {
                    "childProductId": "01tT1000000F0YyIAK",
                    "childSellingModelId": "0jPT10000004CAfMAM",
                    "doesBundlePriceIncludeChild": true,
                    "id": "0dST100000000rgMAA",
                    "isComponentRequired": false,
                    "isDefaultComponent": false,
                    "isQuantityEditable": true,
                    "maxQuantity": 3,
                    "minQuantity": 1,
                    "parentProductId": "01tT1000000F0afIAC",
                    "parentSellingModelId": "0jPT10000004CAfMAM",
                    "productRelationshipTypeId": "0yoT1000000002WIAQ",
                    "quantity": 1,
                    "quantityScaleMethod": "Proportional",
                    "sequence": 1,
                    "isExcluded": false
                  },
                  "productSellingModelOptions": [
                    {
                      "id": "0iOT10000004CMrMAM",
                      "productId": "01tT1000000F0YyIAK",
                      "isDefault": false,
                      "productSellingModel": {
                        "id": "0jPT10000004CAfMAM",
                        "name": "OneTimePSM",
                        "sellingModelType": "OneTime",
                        "status": "Active"
                      }
                    }
                  ],
                  "productSpecificationType": {
                    "name": "NonCommercialSpecType",
                    "productSpecificationRecordType": null
                  }
                }
              ],
              "description": "PCG001 Description",
              "id": "0y7T10000004C9DIAU",
              "maxBundleComponents": 5,
              "minBundleComponents": 1,
              "name": "PCG001",
              "parentProductId": "01tT1000000F0afIAC",
              "sequence": 1,
              "isExcluded": false
            }
          ],
          "productSellingModelOptions": [
            {
              "id": "0iOT10000004CMmMAM",
              "productId": "01tT1000000F0afIAC",
              "productSellingModel": {
                "id": "0jPT10000004CAfMAM",
                "name": "OneTimePSM",
                "sellingModelType": "OneTime",
                "status": "Active"
              }
            }
          ],
          "productSpecificationType": {
            "name": "NonCommercialSpecType",
            "productSpecificationRecordType": null
          }
        }
      ],
      "status": {
        "code": "200",
        "correlationId": "fd158d80-d73c-4a1f-a009-9225db804d70",
        "errors": [],
        "message": "Successfully fetched Product records."
      }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `additional​Fields` | Map<String, [Additional Fields Input](./connect_requests_product_catalog_additional_fields_input.htm.md "Input representation of the additional standard or custom fields to be included in the response.")> | Key-value pair of additional standard or custom fields with their values. | Small, 61.0 | 61.0 |
| `attribute​Category` | [Attribute Category](./connect_responses_attribute_category_output.htm.md "Output representation of the attribute category.")[] | List of categorized attributes related to the product. | Small, 60.0 | 60.0 |
| `attributes` | [Attribute Definition](./connect_responses_attribute_definition_output.htm.md "Output representation of the attribute definition.")[] | List of uncategorized attributes related to the product. | Small, 60.0 | 60.0 |
| `availability​Date` | String | Date when the part is used in the product or is made available for sale. | Small, 60.0 | 60.0 |
| `catalogs` | [Catalog](./connect_responses_catalog_output.htm.md "Output representation of the catalog definition.")[] | List of the associated catalogs returned with the Product List API (POST) response. The Product By ID API (GET) returns an empty catalog list in the response.  Returns the `name` and `id` values only. | Small, 61.0 | 61.0 |
| `categories` | [Category](./connect_responses_category_output.htm.md "Output representation of the category definition.")[] | List of the associated categories returned with the Product List API (POST) response. The Product By ID API (GET) returns an empty category list in the response.  Returns the `name` and `id` values only. | Small, 60.0 | 60.0 |
| `child​Products` | [Product](# "Output representation of the product definition.")[] | Hierarchy of the child products. | Small, 60.0 | 60.0 |
| `configure​During​Sale` | String | Determines whether to allow or prevent configuration when a bundle is sold. | Small, 60.0 | 60.0 |
| `description` | String | Description of the product. If data translation is set up and specified in the org, the translated description is available. | Small, 60.0 | 60.0 |
| `discontinued​Date` | String | Date from when the part can’t be used in the product or sold. | Small, 60.0 | 60.0 |
| `display​Url` | String | Display image URL of the product. | Small, 60.0 | 60.0 |
| `endOf​Life​Date` | String | Date after which a product isn’t supported, ordered, or maintained. | Small, 60.0 | 60.0 |
| `id` | String | ID of the product. | Small, 60.0 | 60.0 |
| `isActive` | Boolean | Indicates if the product is active (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `is​Assetizable` | Boolean | Indicates if the product instance remains a customer asset after it's purchased (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `is​SoldOnly​WithOther​Prods` | Boolean | Indicates whether the product can't be sold separately (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `name` | String | Name of the product. If data translation is set up and specified in the org, the translated name is available. | Small, 60.0 | 60.0 |
| `node​Type` | String | Type of the node, such as a product or bundled product. | Small, 60.0 | 60.0 |
| `product​Classification` | [Product Classification](./connect_responses_product_classification_output.htm.md "Output representation of the product classification details.") | Details of the product classification that the product is based on. | Small, 60.0 | 60.0 |
| `product​Code` | String | Universal product code that's used to track the part that’s used in the product. | Small, 60.0 | 60.0 |
| `product​Component​Groups` | [Product Component Group](./connect_responses_product_component_group_output.htm.md "Output representation of the product component group.")[] | Logical grouping of the component products in a bundle and the group cardinality for ordering the product components. | Small, 60.0 | 60.0 |
| `product​Related​Component` | [Product Related Component](./connect_responses_product_related_component_output.htm.md "Output representation of the product-related component.") | Details of the related components of a product. | Small, 60.0 | 60.0 |
| `product​Selling​Model​Options` | [Product Selling Model Option](./connect_responses_product_selling_model_option_output.htm.md "Output representation of the definition of the product selling model option.")[] | Details of the product selling model options. | Small, 60.0 | 60.0 |
| `product​Specification​Type` | [Product Specification Type](./connect_responses_product_specification_type_output.htm.md "Output representation of the product specification type.") | Details of the product specification type. | Small, 60.0 | 60.0 |
| `quantity​Scale​Method` | String | Method to scale the quantity of the child product in relation to the quantity of the parent. | Small, 60.0 | 60.0 |
