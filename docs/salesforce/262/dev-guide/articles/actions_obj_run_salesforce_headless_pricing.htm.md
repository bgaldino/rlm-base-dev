---
page_id: actions_obj_run_salesforce_headless_pricing.htm
title: Run Salesforce Headless Pricing Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_run_salesforce_headless_pricing.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Run Salesforce Headless Pricing Action

Invoke the Pricing Connect API by providing the pricing data and
details of a context, pricing procedure, and price waterfall.

This action is available in API version 60.0 and later.

## Special Access Rules

The Run Salesforce Headless Pricing action is available in Enterprise, Unlimited, and
Developer Editions where Salesforce Pricing is enabled.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/runSalesforceHeadlessPricing`

Formats
:   JSON, XML

HTTP Methods
:   POST

Authentication
:   `Authorization: Bearer
    token`

## Inputs

| Input | Details |
| --- | --- |
| contextDefinitionId | Type  string  Description  Required.  ID of the context definition record that’s used to build the pricing data. |
| contextMappingId | Type  string  Description  Required.  ID of the context-mapping record that identifies which Salesforce object and mappings to use to build the pricing data. |
| discoveryProcedure | Type  string  Description  Name of the discovery procedure that’s used to execute the discovery process. |
| displayContext | Type  boolean  Description  Indicates whether to display the context structure for pricing (`true`) or not (`false`). |
| effectiveDate | Type  string  Description  Date when the pricing rules, as specified in the pricing procedure, are applied.  The effectiveDate parameter determines which pricing procedure to execute when multiple active versions of pricing procedures are available with different date ranges. |
| isHighVolumeLineItems | Type  boolean  Description  Indicates whether the pricing API returns pricing details for more than 100 line items (`true`) or not (`false`). |
| isSkipWaterfall | Type  boolean  Description  Indicates whether to generate the price waterfall data (`true`) or not (`false`). |
| persistContext | Type  boolean  Description  Indicates whether to store the context (`true`) or not (`false`). If set to `true`, the user must have edit access to all sObject fields used in the context mapping. |
| pricingData | Type  string  Description  Required.  JSON data that’s used to build the pricing data. The JSON must be escaped. If you're using this data within a Flow, then the JSON data must not be escaped. Also, make sure that the `businessObjectType` value within the pricingData property node is set to the sObject used in the context mappings. |
| pricingProcedureId | Type  string  Description  Required.  ID or API name of the pricing procedure used for calculating the prices. A pricing procedure is represented as an Expression Set Definition in the system.  If you’re an Experience Cloud user, specify the name of the pricing procedure. |
| skipDiscovery | Type  boolean  Description  Indicates whether to skip executing the discovery procedure (`true`) or not (`false`). |
| taggedData | Type  boolean  Description  Indicates whether the associated context node contains a key (`true`) or not (`false`). |
| useSessionScopedContext | Type  boolean  Description  Indicates whether to store the context in a session (`true`) or a request (`false`). |

## Outputs

| Output | Details |
| --- | --- |
| contextDetails | Type  string  Description  Context structure for pricing that’s generated when the displayContext parameter is set to `true`. |
| executionId | Type  string  Description  ID of the executed pricing data. |
| pricingProcessErrors | Type  string  Description  Errors that are generated due to context tags in a pricing process. |
| pricingProcessStatus | Type  string  Description  Status of the pricing process, which is executed as an API call. |
| pricingResult | Type  string  Description  Outcome of the executed pricing process that’s based on the output tags defined in the associated context definition. |

## Example

POST
:   This sample request is for the Run Salesforce Headless Pricing action.

    ```
    {
      "inputs": [
        {
          "contextMappingId": "11jSB000002Bn13YAC",
          "contextDefinitionId": "11OSB0000000WSv2AM",
          "pricingProcedureId": "9QLSB0000001lT74AI",
          "discoveryProcedure": "ES1",
          "displayContext": true,
          "effectiveDate": "2023-11-16T12:20:00.000Z",
          "isHighVolumeLineItems": true,
          "skipDiscovery": true,
          "taggedData": false,
          "pricingData": "{\"SalesTransaction\":{\"businessObjectType\":\"SalesTransaction\",\"Pricebook\":\"01sDE0000000LoeYAE\",\"CurrencyIsoCode\":\"USD\",\"SalesTransactionItem\":[{\"businessObjectType\":\"SalesTransactionItem\",\"Product\":\"01tDE000000FU99YAG\",\"ProductSellingModel\":\"0jPDE000000042K2AQ\",\"Quantity\":5,\"StartDate\":\"2023-11-16T12:20:00.000Z\",\"SalesTransactionItemSource\":\"LINE_ITEM1\"}]}}",
          "isSkipWaterfall": false,
          "persistContext": true,
          "useSessionScopedContext": false
        }
      ]
    }
    ```

    This sample response is for the Run Salesforce Headless Pricing action.

    ```
    {
      "actionName": "runSalesforceHeadlessPricing",
      "errors": null,
      "isSuccess": true,
      "outputValues": {
        "contextDetails": {
          "SalesTransaction": [
            {
              "PriceBooks": "01sxx0000005q3VAAQ",
              "Subtotal": 587.2095,
              "PriceAdjustmentSchedule": "84Xxx0000004CMxEAM",
              "EffectiveDate": "2024-02-12T00:00:00.000Z",
              "SalesTransactionItem": [
                {
                  "LineItemQuantity": 5,
                  "ProductSellingModel": "0jPxx000000009hEAA",
                  "DerivedPricingAttribute": false,
                  "Product": "01txx0000006iLwAAI",
                  "LineItem": "LineItem1",
                  "NetUnitPrice": 117.4419,
                  "SalesTrxnAdjustmentGroup": [
                    {
                      "AdjustmentType": "Percentage",
                      "AdjustmentValue": 10
                    }
                  ]
                }
              ]
            }
          ]
        },
        "executionId": "1708488641379821",
        "pricingProcessStatus": "Completed",
        "pricingResult": {
          "StartDate": [
            {
              "value": 1700137200000,
              "dataPath": [
                "CTX_ece1667e-7a09-40ab-9718-23bdc179a0a5",
                "CTX_d3b9ffd5-2be7-4366-92d8-c2bcf03b69ed"
              ],
              "errors": [],
              "isSuccess": true
            }
          ],
          "NetUnitPrice": [
            {
              "value": 115,
              "dataPath": [
                "CTX_ece1667e-7a09-40ab-9718-23bdc179a0a5",
                "CTX_d3b9ffd5-2be7-4366-92d8-c2bcf03b69ed"
              ],
              "errors": [],
              "isSuccess": true
            }
          ],
          "ProductSellingModel": [
            {
              "value": "0jPDE000000042K2AQ",
              "dataPath": [
                "CTX_ece1667e-7a09-40ab-9718-23bdc179a0a5",
                "CTX_d3b9ffd5-2be7-4366-92d8-c2bcf03b69ed"
              ],
              "errors": [],
              "isSuccess": true
            }
          ],
          "Pricebook": [
            {
              "value": "01sDE0000000LoeYAE",
              "dataPath": [
                "CTX_ece1667e-7a09-40ab-9718-23bdc179a0a5"
              ],
              "errors": [],
              "isSuccess": true
            }
          ],
          "NetTotalPrice": [
            {
              "value": 1150,
              "dataPath": [
                "CTX_ece1667e-7a09-40ab-9718-23bdc179a0a5",
                "CTX_d3b9ffd5-2be7-4366-92d8-c2bcf03b69ed"
              ],
              "errors": [],
              "isSuccess": true
            }
          ],
          "Subtotal": [
            {
              "value": 1150,
              "dataPath": [
                "CTX_ece1667e-7a09-40ab-9718-23bdc179a0a5"
              ],
              "errors": [],
              "isSuccess": true
            }
          ],
          "Quantity": [
            {
              "value": 10,
              "dataPath": [
                "CTX_ece1667e-7a09-40ab-9718-23bdc179a0a5",
                "CTX_d3b9ffd5-2be7-4366-92d8-c2bcf03b69ed"
              ],
              "errors": [],
              "isSuccess": true
            }
          ],
          "Product": [
            {
              "value": "01tDE000000FU99YAG",
              "dataPath": [
                "CTX_ece1667e-7a09-40ab-9718-23bdc179a0a5",
                "CTX_d3b9ffd5-2be7-4366-92d8-c2bcf03b69ed"
              ],
              "errors": [],
              "isSuccess": true
            }
          ],
          "CurrencyIsoCode": [
            {
              "value": "USD",
              "dataPath": [
                "CTX_ece1667e-7a09-40ab-9718-23bdc179a0a5"
              ],
              "errors": [],
              "isSuccess": true
            }
          ]
        }
      },
      "version": 1
    }
    ```

#### See Also

- [Salesforce Help: Invoke Salesforce Headless Pricing in a Flow](https://help.salesforce.com/s/articleView?id=ind.pricing_invoke_salesforce_headless_pricing_flow.htm&type=5&language=en_US "Salesforce Help: Invoke Salesforce Headless Pricing in a Flow - HTML (New Window)")
