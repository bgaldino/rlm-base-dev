---
page_id: connect_responses_configurator_attribute_output.htm
title: Configurator Attribute
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_configurator_attribute_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Configurator Attribute

Output representation of the attribute in a product configuration.

JSON example
:   ```
        "attributeCategories": [
          {
            "attributes": [
              {
                "attributeCategoryId": "0v3xx0000000001AAA",
                "attributeNameOverride": "Load Capacity",
                "code": "CAP",
                "dataType": "NUMBER",
                "defaultValue": "1500",
                "description": "Server racks are designed to support a specific load capacity, commonly measured in kilograms (kg) or pounds (lbs). Typical load capacities range from 500 kg (1102 lbs) to 1500 kg (3307 lbs) depending on the model.",
                "id": "0tjxx00000001DpAAI",
                "isCloneable": false,
                "isConfigurable": true,
                "isHidden": false,
                "isPriceImpacting": false,
                "isReadOnly": false,
                "isRequired": false,
                "label": "Load Capacity",
                "name": "Load Capacity"
              },
              {
                "attributeCategoryId": "0v3xx0000000001AAA",
                "attributeNameOverride": "Expansion Slots",
                "code": "SLOTCAP",
                "dataType": "NUMBER",
                "defaultValue": "12",
                "id": "0tjxx00000001H3AAI",
                "isCloneable": false,
                "isConfigurable": true,
                "isHidden": false,
                "isPriceImpacting": false,
                "isReadOnly": false,
                "isRequired": true,
                "label": "Expansion Slots",
                "name": "Expansion Slots"
              },
              {
                "attributeCategoryId": "0v3xx0000000001AAA",
                "attributeNameOverride": "Memory",
                "attributePicklist": {
                  "id": "0v5xx0000000001AAA",
                  "values": [
                    {
                      "code": "MEM",
                      "displayValue": "25",
                      "id": "0v6xx0000000001AAA",
                      "isBooleanValue": false,
                      "name": "25Mem",
                      "sequence": 0,
                      "textValue": "25"
                    },
                    {
                      "code": "50MEM",
                      "displayValue": "50",
                      "id": "0v6xx000000001eAAA",
                      "isBooleanValue": false,
                      "name": "50Mem",
                      "sequence": 1,
                      "textValue": "50"
                    },
                    {
                      "code": "100MEM",
                      "displayValue": "100",
                      "id": "0v6xx000000003FAAQ",
                      "isBooleanValue": false,
                      "name": "100Mem",
                      "sequence": 2,
                      "textValue": "100"
                    }
                  ]
                },
                "dataType": "MULTIPICKLIST",
                "defaultValue": "25",
                "id": "0tjxx00000001IfAAI",
                "isCloneable": false,
                "isConfigurable": true,
                "isHidden": false,
                "isPriceImpacting": false,
                "isReadOnly": false,
                "isRequired": true,
                "label": "Memory",
                "name": "Memory"
              }
            ],
            "code": "SPEC",
            "name": "Server Rack Specifications"
          }
        ],
        "description": "Introducing the Cisco Server Rack, a sleek and robust solution designed to streamline your data center infrastructure. With its scalable design and advanced cable management features, it ensures optimal performance, efficiency, and easy maintenance for your critical network equipment.",
        "displayUrl": "https://www.cisco.com/content/dam/en/us/products/servers-unified-computing/ucs-c240-m4-rack-server/product-large.jpg",
        "id": "01txx0000006jkuAAA",
        "isActive": true,
        "isAssetizable": true,
        "isConfigurable": true,
        "isSoldOnlyWithOtherProds": false,
        "name": "Cisco Server Rack NX44",
        "nodeType": "bundleProduct",
        "prices": [],
        "productClassification": {
          "id": "11Bxx000002CC02EAG"
        },
        "productCode": "RACK",
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
        ],
        "productSellingModelOptions": [
          {
            "id": "0iOxx000000003FEAQ",
            "productId": "01txx0000006jkuAAA",
            "productSellingModel": {
              "id": "0jPxx000000001dEAA",
              "name": "One Time",
              "sellingModelType": "OneTime",
              "status": "Active"
            },
            "productSellingModelId": "0jPxx000000001dEAA"
          },
          {
            "id": "0iOxx000000004rEAA",
            "productId": "01txx0000006jkuAAA",
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
            "id": "0iOxx000000006TEAQ",
            "productId": "01txx0000006jkuAAA",
            "productSellingModel": {
              "id": "0jPxx000000004rEAA",
              "name": "Termed Annually",
              "pricingTerm": 1,
              "pricingTermUnit": "Annual",
              "sellingModelType": "TermDefined",
              "status": "Active"
            },
            "productSellingModelId": "0jPxx000000004rEAA"
          }
        ],
        "productType": "Bundle"
      },
      "errors": [],
      "success": true,
      "transactionContext": {
        "SalesTransaction": [
          {
            "Status": "Draft",
            "Account": "001xx000003GeIxAAK",
            "BillingCity": "San Francisco",
            "Subtotal": 152500,
            "LastPricedDate": "2023-08-22T05:55:39Z",
            "businessObjectType": "Quote",
            "TotalAmount": 152500,
            "ShippingStreet": "415 Mission St",
            "SalesTransactionItem": [
              {
                "ProrationPolicy": null,
                "Discount": null,
                "ProductSellingModel": "0jPxx000000001dEAA",
                "Product": "01txx0000006jkuAAA",
                "businessObjectType": "QuoteLineItem",
                "BasisTransactionItem": null,
                "PartnerUnitPrice": null,
                "StartingUnitPriceSource": "System",
                "ListPrice": 150000,
                "ItemTotalAdjustmentAmount": 0,
                "SalesTransactionItemSource": "0QLxx0000004CQmGAM",
                "SubscriptionTerm": null,
                "StartDate": null,
                "NetTotalPrice": 150000,
                "TotalLineAmount": 150000,
                "PeriodBoundaryStartMonth": null,
                "ListPriceTotal": 150000,
                "PartnerDiscountPercent": null,
                "id": "0QLxx0000004CQmGAM",
                "PriceWaterFall": "{
                    "currencyCode":"USD",
                    "executionEndTimestamp":"2023-09-18T20:11:15.016Z",
                    "executionId":"ruepwmHn2ZFvnQo5bjot",
                    "executionStartTimestamp":"2023-09-18T20:11:14.906Z",
                    "lineItemId":"0QLxx0000004CQmGAM",
                    "output":{
                        "NetUnitPrice":150000.0,
                        "Subtotal":0.0
                     },
                    "success":true,
                    "waterfall":[
                    {
                    "fieldToTagNameMapping":{
                    "NetUnitPrice":"ItemUnitPrice",
                    "AdjustmentValue":"ItemAdjustmentValue",
                    "Subtotal":"ItemTotalAdjustmentAmount",
                    "Quantity":"ItemQuantity",
                    "LineItemId":"SalesTransactionItemSource",
                    "InputUnitPrice":"ItemUnitPrice"
                    },
                    "inputParameters":{
                        "Quantity":1.0,
                        "LineItemId":"0QLxx0000004CQmGAM",
                        "InputUnitPrice":150000.0,
                        "AdjustmentType":"Amount"
                    },
                    "outputParameters":{
                        "NetUnitPrice":150000.0,
                        "Subtotal":0.0
                    },
                "pricingElement":{
                    "adjustments":[
                      {
                        "AdjustmentType":"Amount"
                      }
                  ],
                "elementType":"MANUALDISCOUNT",
                "name":"ManualDiscount"
                },
                "sequence":1
                }
                ]
                }",
                "BillingFrequency": null,
                "SalesTransactionItemParent": "0Q0xx0000004CAeCAM",
                "StartingPriceTotal": 150000,
                "Quantity": 1,
                "PeriodBoundary": null,
                "SalesTransactionItemAttribute": [
                  {
                    "AttributeKey": "0tjxx00000001H3AAI",
                    "AttributeValue": "30.0",
                    "AttributePicklistValue": null,
                    "IsPriceImpacting": true,
                    "businessObjectType": "QuoteLineItemAttribute",
                    "AttributeName": "Expansion Slots",
                    "AttributeDefinitionCode": "SLOTCAP",
                    "id": "0zuxx0000000001AAA",
                    "SalesTransactionItemAttrParent": "0QLxx0000004CQmGAM"
                  }
                ],
                "EndDate": null,
                "DiscountAmount": null,
                "PricebookEntry": "01uxx0000009154AAA",
                "PricingTermCount": 1,
                "NetUnitPrice": 150000,
                "UnitPrice": 150000,
                "StartingUnitPrice": 150000,
                "SalesTrxnItemRelationship": [
                  {
                    "ProductRelationshipType": "0yoxx00000001IfAAI",
                    "MainItemRole": "Bundle",
                    "AssociatedItem": "0QLxx0000004CQnGAM",
                    "ProductRelatedComponent": "0dSxx0000000001EAA",
                    "MainItem": "0QLxx0000004CQmGAM",
                    "AssociatedQuantScaleMethod": "Proportional",
                    "businessObjectType": "QuoteLineRelationship",
                    "AssociatedItemRole": "BundleComponent",
                    "SalesTrnItemRelationshipParent": "0Q0xx0000004CAeCAM",
                    "id": "0yQxx000000001dEAA",
                    "AssociatedItemPricing": "NotIncludedInBundlePrice"
                  }
                ],
                "TotalPrice": 150000,
                "PeriodBoundaryDay": null
              },
              {
                "ProrationPolicy": null,
                "Discount": null,
                "ProductSellingModel": "0jPxx000000001dEAA",
                "Product": "01txx0000006jjIAAQ",
                "businessObjectType": "QuoteLineItem",
                "BasisTransactionItem": null,
                "PartnerUnitPrice": null,
                "StartingUnitPriceSource": "System",
                "ListPrice": 2000,
                "ItemTotalAdjustmentAmount": 0,
                "SalesTransactionItemSource": "0QLxx0000004CQnGAM",
                "SubscriptionTerm": null,
                "StartDate": null,
                "NetTotalPrice": 2000,
                "TotalLineAmount": 2000,
                "PeriodBoundaryStartMonth": null,
                "ListPriceTotal": 2000,
                "PartnerDiscountPercent": null,
                "id": "0QLxx0000004CQnGAM",
                "PriceWaterFall": "{
                    "currencyCode":"USD",
                    "executionEndTimestamp":"023-09-18T20:11:15.016Z",
                    "executionId":"ruepwmHn2ZFvnQo5bjot",
                    "executionStartTimestamp":"2023-09-18T20:11:14.906Z",
                    "lineItemId":"0QLxx0000004CQnGAM",
                    "output":{
                        "NetUnitPrice":2000.0,
                        "Subtotal":0.0
                     },
                    "success":true,
                    "waterfall":[
                    {
                    "fieldToTagNameMapping":{
                    "NetUnitPrice":"ItemUnitPrice",
                    "AdjustmentValue":"ItemAdjustmentValue",
                    "Subtotal":"ItemTotalAdjustmentAmount",
                    "Quantity":"ItemQuantity",
                    "LineItemId":"SalesTransactionItemSource",
                    "InputUnitPrice":"ItemUnitPrice"
                    },
                    "inputParameters":{
                        "Quantity":1.0,
                        "LineItemId":"0QLxx0000004CQnGAM",
                        "InputUnitPrice":2000.0,
                        "AdjustmentType":"Amount"
                    },
                    "outputParameters":{
                        "NetUnitPrice":2000.0,
                        "Subtotal":0.0
                    },
                "pricingElement":{
                    "adjustments":[
                      {}
                  ],
                "elementType":"MANUALDISCOUNT",
                "name":"ManualDiscount"
                },
                "sequence":1
                }
                ]
                }",
                "BillingFrequency": null,
                "SalesTransactionItemParent": "0Q0xx0000004CAeCAM",
                "StartingPriceTotal": 2000,
                "Quantity": 1,
                "PeriodBoundary": null,
                "EndDate": null,
                "DiscountAmount": null,
                "PricebookEntry": "01uxx000000913SAAQ",
                "PricingTermCount": 1,
                "NetUnitPrice": 2000,
                "UnitPrice": 2000,
                "StartingUnitPrice": 2000,
                "TotalPrice": 2000,
                "PeriodBoundaryDay": null
              }
            ],
            "BillingCountry": "US",
            "BillingStreet": "415 Mission St",
            "Pricebook": "01sxx0000005uDZAAY",
            "ShippingPostalCode": "94105",
            "SalesTransactionSource": "0Q0xx0000004CAeCAM",
            "ShippingCountry": "US",
            "ShippingCity": "San Francisco",
            "ShippingState": "CA",
            "BillingPostalCode": "94105",
            "id": "0Q0xx0000004CAeCAM",
            "BillToContact": null,
            "Contract": null,
            "BillingState": "CA"
          }
        ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `attribute​CategoryId` | String | ID of the attribute category. | Small, 60.0 | 60.0 |
| `attribute​NameOverride` | String | Name override value of the attribute. | Small, 60.0 | 60.0 |
| `attribute​Picklist` | [Configurator Attribute Picklist](./connect_responses_configurator_attribute_picklist_output.htm.md "Output representation of the attribute picklist in a product configuration.")[] | Picklist values of the attribute. | Small, 60.0 | 60.0 |
| `code` | String | Code of the attribute. | Small, 60.0 | 60.0 |
| `dataType` | String | Data type of the attribute. | Small, 60.0 | 60.0 |
| `default​HelpText` | String | Default help text value of the attribute. | Small, 60.0 | 60.0 |
| `default​Value` | String | Default value of the attribute. | Small, 60.0 | 60.0 |
| `description` | String | Description of the attribute. | Small, 60.0 | 60.0 |
| `display​Type` | String | Display type of the attribute. | Small, 60.0 | 60.0 |
| `id` | String | ID of the attribute. | Small, 60.0 | 60.0 |
| `is​Cloneable` | Boolean | Indicates if the attribute is cloneable (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `is​Configurable` | Boolean | Indicates if the attribute is configurable (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `isEncrypted` | Boolean | Indicates if the attribute is encrypted (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `isHidden` | Boolean | Indicates if the attribute is hidden (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `isPrice​Impacting` | Boolean | Indicates if this is a price impacting attribute (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `isReadOnly` | Boolean | Indicates if the attribute is read-only (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `isRequired` | Boolean | Indicates if the attribute is required (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `label` | String | Label of the attribute. | Small, 60.0 | 60.0 |
| `maximum​Value` | String | Maximum value for the product attribute. | Small, 60.0 | 60.0 |
| `minimum​Value` | String | Minimum value for the product attribute. | Small, 60.0 | 60.0 |
| `name` | String | Name of the attribute. | Small, 60.0 | 60.0 |
| `sequence` | Integer | Sequence values of the attribute. | Small, 60.0 | 60.0 |
| `status` | String | Status of the attribute. | Small, 60.0 | 60.0 |
| `stepValue` | String | Step value for the attribute. | Small, 60.0 | 60.0 |
| `unitOfMeasure` | [Configurator Unit Of Measure](./connect_responses_configurator_unit_of_measure_output.htm.md "Output representation of the details of the unit of measure record.")[] | Details about the unit of measure associated with an attribute. | Small, 63.0 | 63.0 |
| `userValue` | String | User value of the attribute. | Small, 60.0 | 60.0 |
| `value​Decoder` | String | Value decoder for the attribute. | Small, 60.0 | 60.0 |
| `value​Description` | String | Value description of the attribute. | Small, 60.0 | 60.0 |
