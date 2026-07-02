---
page_id: connect_resources_headless.htm
title: Pricing (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_headless.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_business_apis_rest_references.htm
fetched_at: 2026-06-09
---

# Pricing (POST)

Create and hydrate context instance in a single request. Provide a
comprehensive response that contains final pricing details per line items and related errors,
if any.

If price waterfall is disabled from Salesforce Pricing Setup in your org, this API
doesn't return the waterfall details. You can use the [Price Waterfall API](./connect_resources_pricing_waterfall_fetch.htm.md "HTML (New Window)") to
retrieve the waterfall details if price waterfall persistence is enabled in Salesforce
Pricing Setup.

Resource
:   ```
    /connect/core-pricing/pricing
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/core-pricing/pricing
    ```

Available version
:   60.0

Requires Chatter
:   No

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "contextDefinitionId": "11Oxx0000006PdxEAE",
          "contextMappingId": "11jxx0000004LDDAA2",
          "jsonDataString": {
            "Cart": [
              {
                "id": "cart_1001",
                "cart_id": "cart_1001",
                "PriceBookId": "PriceBookId_1001",
                "businessObjectType": "Cart",
                "CartItem": [
                  {
                    "id": "lineItem_1001",
                    "line_item_id": "lineItem_1001",
                    "Quantity": 7,
                    "PriceType": "OneTime",
                    "Frequency": "",
                    "UOM": "",
                    "businessObjectType": "CartItem",
                    "product_id": "01txx0000006i44AAA",
                    "UnitPrice": 6.8,
                    "NetUnitPrice": 0,
                    "Attribute": [
                      {
                        "name": "Color",
                        "code": "RED",
                        "isPriceImpacting": true,
                        "businessObjectType": "Attribute",
                        "id": "Attribute_1001",
                        "attribute_id": "Attribute_1001"
                      },
                      {
                        "name": "Size",
                        "code": "10INCH",
                        "isPriceImpacting": true,
                        "businessObjectType": "Attribute",
                        "id": "Attribute_1002",
                        "attribute_id": "Attribute_1002"
                      }
                    ]
                  },
                  {
                    "id": "lineItem_1002",
                    "line_item_id": "lineItem_1002",
                    "quantity": 3,
                    "PriceType": "OneTime",
                    "Frequency": "",
                    "UOM": "",
                    "businessObjectType": "CartItem",
                    "product_id": "01txx0000006i2SAAQ",
                    "unitprice": 6,
                    "NetUnitPrice": 0,
                    "Attribute": [
                      {
                        "name": "Color",
                        "code": "BLUE",
                        "isPriceImpacting": true,
                        "businessObjectType": "Attribute",
                        "id": "Attribute_1003",
                        "attribute_id": "Attribute_1003"
                      },
                      {
                        "name": "Size",
                        "code": "6INCH",
                        "isPriceImpacting": true,
                        "businessObjectType": "Attribute",
                        "id": "Attribute_1004",
                        "attribute_id": "Attribute_1004"
                      }
                    ]
                  }
                ]
              }
            ]
          },
          "pricingProcedureId": "9QMxx0000004CKKGA2",
          "configurationOverrides": {
            "skipWaterfall": true,
            "useSessionScopedContext": true,
            "persistContext": true,
            "referenceKey": "referenceKey-12345",
            "displayContext" : false,
            "taggedData": false,
            "isHighVolumeLineItems": false
          }
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `configuration​Overrides` | [Configuration Override Input](./connect_requests_configuration_override_input.htm.md "Input representation of the details to override for a Pricing API configuration.") | Parameters to override the pricing configuration. | Optional | 60.0 |
        | `context​Definition​Id` | String | ID of the context definition that defines the structure of the input data. | Required | 60.0 |
        | `context​Mapping​Id` | String | ID of the context mapping that maps the input data to the context instance. | Required | 60.0 |
        | `json​Data​String` | String | Data to hydrate the context, which must be in JSON format and passed as String. Pass the JSON data as String by using the stringify() method to convert the object to string.  The keys in the jsonDataString property must be in accordance to the contextMappingId property sent in the request.  Make sure that the `businessObjectType` value within this property node is set to the sObject used in the context mappings. | Required | 60.0 |
        | `pricing​Procedure​Id` | String | ID or API name of the pricing procedure used for calculating the prices. A pricing procedure is represented as an Expression Set Definition in the system.  If you’re an Experience Cloud user, specify the name of the pricing procedure. | Optional | 60.0 |

Response body for POST
:   [Pricing Output](./connect_responses_core_pricing_output.htm.md "Output representation of a Salesforce pricing request.")
