---
page_id: actions_obj_submit_order.htm
title: Submit Order Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_submit_order.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Submit Order Action

Submit an order to Dynamic Revenue Orchestrator (DRO) for
fulfillment.

By using the Submit Order action, you can perform:

- Order decomposition
- Fulfillment orchestration that’s driven through message queues
- Dynamic plan composition that’s based on the incoming order

This action is available in API version 61.0 and later.

## Special Access Rules

The Submit Order action is available in Enterprise, Unlimited, and Developer Editions of Revenue
Cloud. See the [required permissions](https://help.salesforce.com/s/articleView?id=ind.dro_permission_sets_in_dynamic_revenue_orchestrator.htm&type=5&language=en_US "HTML (New Window)") to
access and call this invocable action.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/submitOrder`

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
| orderId | Type  string  Description  Required.  ID of the order to submit to DRO. |
| callType | Type  string  Description  Optional.  Mode that the order intake must be processed in. Valid values are:   - `Synchronous` - `Asynchronous`   The default value is `Asynchronous`. |
| contextId | Type  string  Description  Optional.  ID of the hydrated context. See [Context Service](https://developer.salesforce.com/docs/atlas.en-us.262.0.industries_reference.meta/industries_reference/context_service_overview.htm "HTML (New Window)"). |

## Outputs

| Output | Details |
| --- | --- |
| errorCode | Type  string  Description  Error code for the failed request, if any. |
| fulfillmentPlanId | Type  string  Description  ID of the orchestrated fulfillment plan that’s generated. Returned only if the callType value is `Synchronous`. |
| requestId | Type  string  Description  Unique ID of the invocation request that helps identify a single request. |
| submitStatus | Type  string  Description  Submit status of the invocation request. Valid values are:   - `SUCCESS` - `ERROR` - `SUBMITTED` - `REJECTED` |
| usedContextId | Type  string  Description  Hydrated context ID that’s used in this request, which can be different from the contextId input. |

## Example

POST
:   This example shows a sample request.

    ```
    {
        "inputs": [
            {
                "orderId": "801RM0000007yGaYAI",
                "callType": "Synchronous"
            }
        ]
    }
    ```

    This example shows a sample response when the call type is
    synchronous.

    ```
    [
        {
       "actionName":"submitOrder"
       "errors":NULL
       "invocationId":NULL
       "isSuccess":true
       "outputValues":{
       "requestId":"a161cfda-868c-41d2-b589-7c7d7ff2d4c1"
       "submitStatus":"SUCCESS"
       "usedContextId":"e275e930923106ee7e39cbfa232e38252bd4d63f4ea2dd956b7301e243554134"
       "fulfillmentPlanId":"13VZM00000000062AA"
    }
    ]
    ```

    This example shows a sample response when the call type is asynchronous
    or isn’t specified.

    ```
    [
    {
        "actionName": "submitOrder",
        "errors": null,
        "isSuccess": true,
        "outputValues": {
        "submitStatus": "SUBMITTED"
        "requestId": "a161cfda-868c-41d2-b589-7c7d7ff2d4c1"
    }
    }
    ]
    ```

    This example shows a sample response when a validation error occurs.

    ```
    [
        {
        "actionName": "submitOrder",
        "errors": [
        {
            "statusCode": "UNKNOWN_EXCEPTION",
            "message": "Missing required input parameter: orderId",
            "fields": []
         }
      ],
            "invocationId": null,
            "isSuccess": false,
            "outputValues": {
              "requestId": "4c7d8ebb-6b0b-4852-a8a0-b67e0d36a73e",
              "errorCode": "DRO_INTERNAL_ERROR"
            },
        }
    ]
    ```

## Explainability Action Logs

:   To troubleshoot or debug errors, retrieve a list of explainability action logs. See [Action Logs](https://developer.salesforce.com/docs/atlas.en-us.262.0.industries_reference.meta/industries_reference/connect_resources_get_create_action_logs.htm "HTML (New Window)").

Get logs for order intake
:   This resource example includes sample query parameters to retrieve the action logs for an
    order
    intake.

    ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/decision-explainer/action-logs?applicationSubType=DroSubmit&applicationType=7&processType=DroSubmit&primaryFilter=801xx000003GYzvAAG
    ```
:   This example shows the sample response. The actionLog
    property contains the action logs.

    ```
    {
      "actionLogs": [
        {
          "actionContextCode": "801NA000000XKPUYA4",
          "actionLog": {
            "OrderIntakeStatus": "",
            "OrderIntakeStatusMessage": "",
            "OrderId": "801NA000000XKPUYA4",
            "SubmitMode": "Synchronous",
            "UniqueRequestId": "d00c2aa7-56b0-411a-9b51-83d9fe2e4440",
            "ContexId": "a0ca3c2296c82ad071a5efa83e8974793910f44ebddb21d37f007ce4889b65d7",
            "DesActionSpecDevName": "DroSubmitAction",
            "ContextDefinition": "SalesTransactionContext__stdctx"
          },
          "additionalFilter": "undef",
          "applicationLogDate": "Thu Mar 28 12:36:26 GMT 2024",
          "applicationSubtype": "DroSubmit",
          "applicationType": "7",
          "explainabilitySpecName": "DroSubmitAction",
          "isChunked": false,
          "name": "DroSubmitAction",
          "primaryFilter": "801NA000000XKPUYA4",
          "processType": "DroSubmit",
          "secondaryFilter": "undef",
          "uniqueIdentifier": "02c4bae9-d8b0-42f6-b031-e983d4247c76"
        }
      ],
      "queryMore": ""
    }
    ```

Get logs for decomposition scope
:   This resource example includes sample query parameters to retrieve the
    decomposition-related action
    logs.

    ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/decision-explainer/action-logs?applicationSubType=DroDcmp&applicationType=7&processType=DcmpScp&primaryFilter=801xx000003GYzvAAG
    ```
:   This example shows the sample response. The actionLog
    property contains the action logs.

    ```
    {
      "actionLogs": [
        {
          "actionContextCode": "801NA000000XKPeYAO",
          "actionLog": {
            "CandidateDecompositionRules": [
              {
                "decompRuleId": "13UNA0000004C932AE",
                "SourceProductId": "01tNA0000007NP5YAM",
                "AssociatedOlis": [
                  "802NA000002lWjOYAU"
                ],
                "DestinationProductId": "01tNA0000007NOvYAM",
                "DestinationProductScope": "Order",
                "ConfiguredContextRuleId": "null"
              },
              {
                "decompRuleId": "13UNA0000004ITY2A2",
                "SourceProductId": "01tNA0000007NP5YAM",
                "AssociatedOlis": [
                  "802NA000002lWjOYAU"
                ],
                "DestinationProductId": "01tNA0000007NOqYAM",
                "DestinationProductScope": "Order",
                "ConfiguredContextRuleId": "null"
              },
              {
                "decompRuleId": "13UNA0000004C942AE",
                "SourceProductId": "01tNA0000007NPAYA2",
                "AssociatedOlis": [
                  "802NA000002lWjKYAU"
                ],
                "DestinationProductId": "01tNA0000007NOwYAM",
                "DestinationProductScope": "Order",
                "ConfiguredContextRuleId": "null"
              },
              {
                "decompRuleId": "13UNA0000004ITd2AM",
                "SourceProductId": "01tNA0000007NPAYA2",
                "AssociatedOlis": [
                  "802NA000002lWjKYAU"
                ],
                "DestinationProductId": "01tNA0000007NP0YAM",
                "DestinationProductScope": "Order",
                "ConfiguredContextRuleId": "null"
              },
              {
                "decompRuleId": "13UNA0000004C952AE",
                "SourceProductId": "01tNA0000007NPBYA2",
                "AssociatedOlis": [
                  "802NA000002lWjLYAU"
                ],
                "DestinationProductId": "01tNA0000007NOxYAM",
                "DestinationProductScope": "Order",
                "ConfiguredContextRuleId": "9QwNA0000000CTu0AM"
              },
              {
                "decompRuleId": "13UNA0000004C982AE",
                "SourceProductId": "01tNA0000007NPCYA2",
                "AssociatedOlis": [
                  "802NA000002lWjNYAU"
                ],
                "DestinationProductId": "01tNA0000007NOqYAM",
                "DestinationProductScope": "Order",
                "ConfiguredContextRuleId": "null"
              },
              {
                "decompRuleId": "13UNA0000004C992AE",
                "SourceProductId": "01tNA0000007NPCYA2",
                "AssociatedOlis": [
                  "802NA000002lWjNYAU"
                ],
                "DestinationProductId": "01tNA0000007NOrYAM",
                "DestinationProductScope": "Order",
                "ConfiguredContextRuleId": "9QwNA0000000CTt0AM"
              }
            ],
            "SelectedDecompositionRules": [
              {
                "OliId": "802NA000002lWjKYAU",
                "DecompositionRuleIds": [
                  "13UNA0000004C942AE",
                  "13UNA0000004ITd2AM"
                ]
              },
              {
                "OliId": "802NA000002lWjOYAU",
                "DecompositionRuleIds": [
                  "13UNA0000004C932AE",
                  "13UNA0000004ITY2A2"
                ]
              },
              {
                "OliId": "802NA000002lWjNYAU",
                "DecompositionRuleIds": [
                  "13UNA0000004C982AE"
                ]
              }
            ],
            "OliScopeDetails": [
              {
                "OliId": "802NA000002lWjLYAU",
                "ParentOliId": "802NA000002lWjOYAU",
                "BundleRootOli": "802NA000002lWjOYAU"
              },
              {
                "OliId": "802NA000002lWjMYAU",
                "ParentOliId": "802NA000002lWjOYAU",
                "BundleRootOli": "802NA000002lWjOYAU"
              },
              {
                "OliId": "802NA000002lWjKYAU",
                "ParentOliId": "802NA000002lWjOYAU",
                "BundleRootOli": "802NA000002lWjOYAU"
              },
              {
                "OliId": "802NA000002lWjNYAU",
                "ParentOliId": "802NA000002lWjOYAU",
                "BundleRootOli": "802NA000002lWjOYAU"
              }
            ],
            "FoliComputationDetails": [
              {
                "FoliId": "0a4NA000003HYbWYAW",
                "ComputedAction": "AMEND",
                "ComputedQuantity": "3.0"
              },
              {
                "FoliId": "0a4NA000003HYbXYAW",
                "ComputedAction": "AMEND",
                "ComputedQuantity": "6.0"
              },
              {
                "FoliId": "0a4NA000003HYbYYAW",
                "ComputedAction": "AMEND",
                "ComputedQuantity": "3.0"
              },
              {
                "FoliId": "0a4NA000003HYbZYAW",
                "ComputedAction": "AMEND",
                "ComputedQuantity": "3.0"
              }
            ],
            "FlsrDetails": [
              {
                "FlsrId": "16ANA000005idR82AI",
                "FlsrGuid": "WQoYClnAszG9axKxWxoe",
                "SourceId": "802NA000002lWjOYAU",
                "FoliId": "0a4NA000003HYbWYAW"
              },
              {
                "FlsrId": "16ANA000005idR92AI",
                "FlsrGuid": "80xWFpBK8sDmTFRV3Dn0",
                "SourceId": "802NA000002lWjOYAU",
                "FoliId": "0a4NA000003HYbXYAW"
              },
              {
                "FlsrId": "16ANA000005idRA2AY",
                "FlsrGuid": "nAql9VD3KiziZTFrfYXq",
                "SourceId": "802NA000002lWjNYAU",
                "FoliId": "0a4NA000003HYbXYAW"
              },
              {
                "FlsrId": "16ANA000005idRB2AY",
                "FlsrGuid": "wgCJT6NJ3ESolFXP5ajQ",
                "SourceId": "802NA000002lWjKYAU",
                "FoliId": "0a4NA000003HYbYYAW"
              },
              {
                "FlsrId": "16ANA000005idRC2AY",
                "FlsrGuid": "bvVhA34WvTBOYbG4q2Fj",
                "SourceId": "802NA000002lWjKYAU",
                "FoliId": "0a4NA000003HYbZYAW"
              }
            ],
            "OrderId": "801NA000000XKPeYAO",
            "SubmitMode": "Synchronous",
            "UniqueRequestId": "b9ac5971-0d71-45c6-a18e-f472976eaeae",
            "ContextId": "1422049ffa3cc42d8c060b9a7732be360bd62a346652cda9ab6e5fd54cd03eca",
            "DesActionSpecDevName": "DroDecompScopeAction",
            "ContextDefinition": "SalesTransactionContext__stdctx"
          },
          "additionalFilter": "undef",
          "applicationLogDate": "Fri Mar 29 10:02:26 GMT 2024",
          "applicationSubtype": "DroDcmp",
          "applicationType": "7",
          "explainabilitySpecName": "DroDecompScopeAction",
          "isChunked": false,
          "name": "DroDecompScopeAction",
          "primaryFilter": "801NA000000XKPeYAO",
          "processType": "DcmpScp",
          "secondaryFilter": "undef",
          "uniqueIdentifier": "c1e11bc0-53e5-4f62-9ae8-1096e79a62b6"
        }
      ],
      "queryMore": ""
    }
    ```

Get logs for decomposition enrichment
:   This resource example includes sample query parameters to retrieve the logs for
    decomposition enrichment tasks. For example, conversion of order items to fulfillment
    order line
    items.

    ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/decision-explainer/action-logs?applicationSubType=DroDcmp&applicationType=7&processType=DcmpEnrich&primaryFilter=801xx000003GYzvAAG&secondaryFilter=BxyDQUJ2B49CoKXiuvGI
    ```
:   The secondaryFilter property is optional. If this property is
    specified, the API returns the enrichment rule details for a decomposition rule. If this
    property is unspecified, the API returns all enrichment rule details for the order.
:   This example shows the sample response. The actionLog
    property contains the action logs.

    ```
    {
      "actionLogs": [
        {
          "actionContextCode": "801NA000000XKPUYA4",
          "actionLog": {
            "FlsrUid": "1FxfIhMq53OIpE9Hzs5w",
            "EnrichmentRulesExecutionDetails": [
              {
                "EnrichmentRuleId": "13TNA00000000eG2AQ",
                "DecompRuleId": "13UNA0000004C942AE",
                "FlsrUid": "1FxfIhMq53OIpE9Hzs5w",
                "SourceType": "Attribute",
                "SourceAttributeId": "0tjNA0000004CygYAE",
                "TargetType": "Attribute",
                "TargetAttributeId": "0tjNA0000004CyDYAU",
                "CalculationMethod": "Ad-verbatim",
                "ExecutionStatus": "SUCCESS"
              },
              {
                "EnrichmentRuleId": "13TNA00000000eH2AQ",
                "DecompRuleId": "13UNA0000004C942AE",
                "FlsrUid": "1FxfIhMq53OIpE9Hzs5w",
                "SourceType": "Attribute",
                "SourceAttributeId": "0tjNA0000004CylYAE",
                "TargetType": "Attribute",
                "TargetAttributeId": "0tjNA0000004CyIYAU",
                "CalculationMethod": "Ad-verbatim",
                "ExecutionStatus": "SUCCESS"
              },
              {
                "EnrichmentRuleId": "13TNA00000000eI2AQ",
                "DecompRuleId": "13UNA0000004C942AE",
                "FlsrUid": "1FxfIhMq53OIpE9Hzs5w",
                "SourceType": "Attribute",
                "SourceAttributeId": "0tjNA0000004CyqYAE",
                "TargetType": "Attribute",
                "TargetAttributeId": "0tjNA0000004CyhYAE",
                "CalculationMethod": "Ad-verbatim",
                "ExecutionStatus": "SUCCESS"
              },
              {
                "EnrichmentRuleId": "13TNA00000000eJ2AQ",
                "DecompRuleId": "13UNA0000004C942AE",
                "FlsrUid": "1FxfIhMq53OIpE9Hzs5w",
                "SourceType": "Attribute",
                "SourceAttributeId": "0tjNA0000004CzPYAU",
                "TargetType": "Attribute",
                "TargetAttributeId": "0tjNA0000004CymYAE",
                "CalculationMethod": "Ad-verbatim",
                "ExecutionStatus": "SUCCESS"
              },
              {
                "EnrichmentRuleId": "13TNA00000000eK2AQ",
                "DecompRuleId": "13UNA0000004C942AE",
                "FlsrUid": "1FxfIhMq53OIpE9Hzs5w",
                "SourceType": "Attribute",
                "SourceAttributeId": "0tjNA0000004CzUYAU",
                "TargetType": "Attribute",
                "TargetAttributeId": "0tjNA0000004CyrYAE",
                "CalculationMethod": "Ad-verbatim",
                "ExecutionStatus": "SUCCESS"
              },
              {
                "EnrichmentRuleId": "13TNA00000000eL2AQ",
                "DecompRuleId": "13UNA0000004C942AE",
                "FlsrUid": "1FxfIhMq53OIpE9Hzs5w",
                "SourceType": "Attribute",
                "SourceAttributeId": "0tjNA0000004CzZYAU",
                "TargetType": "Attribute",
                "TargetAttributeId": "0tjNA0000004CywYAE",
                "CalculationMethod": "Ad-verbatim",
                "ExecutionStatus": "SUCCESS"
              },
              {
                "EnrichmentRuleId": "13TNA00000000eM2AQ",
                "DecompRuleId": "13UNA0000004C942AE",
                "FlsrUid": "1FxfIhMq53OIpE9Hzs5w",
                "SourceType": "Attribute",
                "SourceAttributeId": "0tjNA0000004D0dYAE",
                "TargetType": "Attribute",
                "TargetAttributeId": "0tjNA0000004Cz1YAE",
                "CalculationMethod": "Ad-verbatim",
                "ExecutionStatus": "ERROR_DATA_TYPE_MISMATCH"
              },
              {
                "EnrichmentRuleId": "13TNA00000000eN2AQ",
                "DecompRuleId": "13UNA0000004C942AE",
                "FlsrUid": "1FxfIhMq53OIpE9Hzs5w",
                "SourceType": "Attribute",
                "SourceAttributeId": "0tjNA0000004D0iYAE",
                "TargetType": "Attribute",
                "TargetAttributeId": "0tjNA0000004CzQYAU",
                "CalculationMethod": "Ad-verbatim",
                "ExecutionStatus": "ERROR_DATA_TYPE_MISMATCH"
              },
              {
                "EnrichmentRuleId": "13TNA00000000eO2AQ",
                "DecompRuleId": "13UNA0000004C942AE",
                "FlsrUid": "1FxfIhMq53OIpE9Hzs5w",
                "SourceType": "Attribute",
                "SourceAttributeId": "0tjNA0000004D18YAE",
                "TargetType": "Attribute",
                "TargetAttributeId": "0tjNA0000004CzVYAU",
                "CalculationMethod": "Ad-verbatim",
                "ExecutionStatus": "ERROR_DATA_TYPE_MISMATCH"
              },
              {
                "EnrichmentRuleId": "13TNA00000000eP2AQ",
                "DecompRuleId": "13UNA0000004C942AE",
                "FlsrUid": "1FxfIhMq53OIpE9Hzs5w",
                "SourceType": "Attribute",
                "SourceAttributeId": "0tjNA0000004D1QYAU",
                "TargetType": "Attribute",
                "TargetAttributeId": "0tjNA0000004CzaYAE",
                "CalculationMethod": "Ad-verbatim",
                "ExecutionStatus": "ERROR_DATA_TYPE_MISMATCH"
              }
            ],
            "OrderId": "801NA000000XKPUYA4",
            "SubmitMode": "Synchronous",
            "UniqueRequestId": "d00c2aa7-56b0-411a-9b51-83d9fe2e4440",
            "ContexId": "a0ca3c2296c82ad071a5efa83e8974793910f44ebddb21d37f007ce4889b65d7",
            "DesActionSpecDevName": "DroDecompEnrichmentAction",
            "ContextDefinition": "SalesTransactionContext__stdctx"
          },
          "additionalFilter": "undef",
          "applicationLogDate": "Thu Mar 28 12:36:25 GMT 2024",
          "applicationSubtype": "DroDcmp",
          "applicationType": "7",
          "explainabilitySpecName": "DroDecompEnrichmentAction",
          "isChunked": false,
          "name": "DroDecompEnrichmentAction",
          "primaryFilter": "801NA000000XKPUYA4",
          "processType": "DcmpEnrich",
          "secondaryFilter": "1FxfIhMq53OIpE9Hzs5w",
          "uniqueIdentifier": "0bd42942-12b2-4c2e-9f10-b77ee85fd20b"
        }
      ],
      "queryMore": ""
    }
    ```

Get logs for plan composition
:   This resource example includes sample query parameters to retrieve the logs for plan
    composition.

    ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/decision-explainer/action-logs?applicationSubType=DroPcmp&applicationType=7&processType=PcmpSteps&primaryFilter=801xx000003GYzvAAG
    ```
:   This example shows the sample response. The actionLog
    property contains the action logs.

    ```
    {
      "actionLogs": [
        {
          "actionContextCode": "801NA000000XKPeYAO",
          "actionLog": {
            "PlanCompositionStatus": "",
            "PlanCompositionStatusMessage": "",
            "CandidateProductFulfillmentScenarios": [
              {
                "ProductFulfillmentScenarioId": "1axNA0000004C93YAE",
                "ProductId": "01tNA0000007NP5YAM",
                "FulfillmentStepDefinitionGroupId": "13oNA0000004CARYA2",
                "LineItemIds": [
                  "802NA000002lWjOYAU"
                ],
                "ContextRulesetId": "9QwNA0000000CXq0AM"
              }
            ],
            "SelectedProductFulfillmentScenarios": [
              null
            ],
            "SelectedProductFulfillmentScenariosByOli": [
              {
                "OliId": "0a4NA000003HYbFYAW",
                "ProductFulfillmentScenarios": [
                  null
                ]
              },
              {
                "OliId": "0a4NA000003HYbXYAW",
                "ProductFulfillmentScenarios": [
                  null
                ]
              },
              {
                "OliId": "0a4NA000003HYbIYAW",
                "ProductFulfillmentScenarios": [
                  null
                ]
              },
              {
                "OliId": "802NA000002lWjOYAU",
                "ProductFulfillmentScenarios": [
                  null
                ]
              }
            ],
            "PlanId": "13VNA000000OQ9W2AW",
            "FulfillmentStepCreationStatus": "FulfillmentStepsCreated",
            "FulfillmentStepDependencyCreationStatus": "FulfilmentStepDepCreated",
            "OrderId": "801NA000000XKPeYAO",
            "SubmitMode": "Synchronous",
            "UniqueRequestId": "b9ac5971-0d71-45c6-a18e-f472976eaeae",
            "ContextId": "1422049ffa3cc42d8c060b9a7732be360bd62a346652cda9ab6e5fd54cd03eca",
            "DesActionSpecDevName": "DroPlanCompStepsAction",
            "ContextDefinition": "SalesTransactionContext__stdctx"
          },
          "additionalFilter": "undef",
          "applicationLogDate": "Fri Mar 29 10:02:27 GMT 2024",
          "applicationSubtype": "DroPcmp",
          "applicationType": "7",
          "explainabilitySpecName": "DroPlanCompStepsAction",
          "isChunked": false,
          "name": "DroPlanCompStepsAction",
          "primaryFilter": "801NA000000XKPeYAO",
          "processType": "PcmpSteps",
          "secondaryFilter": "undef",
          "uniqueIdentifier": "bb532c9b-a88f-4add-8cd8-bd385359b1ad"
        }
      ],
      "queryMore": ""
    }
    ```

Capture logs for an order
:   This resource example includes sample query parameters to retrieve the logs for an
    order.

    ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/decision-explainer/action-logs?actionContextCode=801DU000000CqBJYA0&applicationType=7
    ```
:   This example shows the sample response. The actionLog property
    contains the action logs.

    ```
    {
      "actionLogs": [
        {
          "actionContextCode": "801xx000003GZSxAAO",
          "actionLog": "{&quot;FlsrUid&quot;:&quot;qrh0Z3xv6buew1BW0wdn&quot;,&quot;DecompositionEnrichmentExecutionSequence&quot;:&quot;0&quot;,&quot;EnrichmentRulesExecutionDetails&quot;:[{&quot;EnrichmentRuleId&quot;:&quot;13Txx0000004CLwEAM&quot;,&quot;DecompRuleId&quot;:&quot;13Uxx0000004CCGEA2&quot;,&quot;FlsrUid&quot;:&quot;qrh0Z3xv6buew1BW0wdn&quot;,&quot;SourceType&quot;:&quot;Attribute&quot;,&quot;SourceAttributeId&quot;:&quot;0tjxx0000000001AAA&quot;,&quot;TargetType&quot;:&quot;Attribute&quot;,&quot;TargetAttributeId&quot;:&quot;0tjxx0000000085AAA&quot;,&quot;CalculationMethod&quot;:&quot;Ad-verbatim&quot;,&quot;ExecutionStatus&quot;:&quot;ERROR_SOURCE_DATA_FETCH&quot;},{&quot;EnrichmentRuleId&quot;:&quot;13Txx0000004CNYEA2&quot;,&quot;DecompRuleId&quot;:&quot;13Uxx0000004CCGEA2&quot;,&quot;FlsrUid&quot;:&quot;qrh0Z3xv6buew1BW0wdn&quot;,&quot;SourceType&quot;:&quot;Field&quot;,&quot;SourceFieldName&quot;:&quot;Product2Id&quot;,&quot;SourceContextTag&quot;:&quot;Product&quot;,&quot;TargetType&quot;:&quot;Attribute&quot;,&quot;TargetAttributeId&quot;:&quot;0tjxx000000006TAAQ&quot;,&quot;CalculationMethod&quot;:&quot;Ad-verbatim&quot;,&quot;ExecutionStatus&quot;:&quot;SUCCESS&quot;},{&quot;EnrichmentRuleId&quot;:&quot;13Txx0000004CPAEA2&quot;,&quot;DecompRuleId&quot;:&quot;13Uxx0000004CCGEA2&quot;,&quot;FlsrUid&quot;:&quot;qrh0Z3xv6buew1BW0wdn&quot;,&quot;SourceType&quot;:&quot;Field&quot;,&quot;SourceFieldName&quot;:&quot;IsAssetizable&quot;,&quot;SourceContextTag&quot;:&quot;IsAssetizable&quot;,&quot;TargetType&quot;:&quot;Attribute&quot;,&quot;TargetAttributeId&quot;:&quot;0tjxx000000004rAAA&quot;,&quot;CalculationMethod&quot;:&quot;Ad-verbatim&quot;,&quot;ExecutionStatus&quot;:&quot;SUCCESS&quot;},{&quot;EnrichmentRuleId&quot;:&quot;13Txx0000004CQmEAM&quot;,&quot;DecompRuleId&quot;:&quot;13Uxx0000004CCGEA2&quot;,&quot;FlsrUid&quot;:&quot;qrh0Z3xv6buew1BW0wdn&quot;,&quot;SourceType&quot;:&quot;Attribute&quot;,&quot;SourceAttributeId&quot;:&quot;0tjxx000000001dAAA&quot;,&quot;TargetType&quot;:&quot;Attribute&quot;,&quot;TargetAttributeId&quot;:&quot;0tjxx000000003FAAQ&quot;,&quot;CalculationMethod&quot;:&quot;Ad-verbatim&quot;,&quot;ExecutionStatus&quot;:&quot;ERROR_SOURCE_DATA_FETCH&quot;}],&quot;OrderId&quot;:&quot;801xx000003GZSxAAO&quot;,&quot;SubmitMode&quot;:&quot;Synchronous&quot;,&quot;UniqueRequestId&quot;:&quot;5dd3888e-e883-4770-b0ad-aa59e88450eb&quot;,&quot;ContextId&quot;:&quot;d9995de15eea0b3c1ed0a552813fe9cd02b73d0de80c0c15fd4e8ac6661508df&quot;,&quot;DesActionSpecDevName&quot;:&quot;DroDecompEnrichmentAction&quot;,&quot;ContextDefinition&quot;:&quot;SalesTransactionContext__stdctx&quot;}",
          "additionalFilter": "undef",
          "applicationLogDate": "Tue May 07 13:05:28 GMT 2024",
          "applicationSubtype": "DroDcmp",
          "applicationType": "7",
          "explainabilitySpecName": "DroDecompEnrichmentAction",
          "isChunked": false,
          "name": "DroDecompEnrichmentAction",
          "primaryFilter": "801xx000003GZSxAAO",
          "processType": "DcmpEnrich",
          "secondaryFilter": "qrh0Z3xv6buew1BW0wdn",
          "uniqueIdentifier": "768f7d03-6770-4939-980f-a6f42ad07cde"
        },
        {
          "actionContextCode": "801xx000003GZSxAAO",
          "actionLog": "{&quot;FlsrUid&quot;:&quot;hjow5L3YcntZsnNuEd5n&quot;,&quot;DecompositionEnrichmentExecutionSequence&quot;:&quot;0&quot;,&quot;EnrichmentRulesExecutionDetails&quot;:[{&quot;EnrichmentRuleId&quot;:&quot;13Txx0000004CH6EAM&quot;,&quot;DecompRuleId&quot;:&quot;13Uxx0000004CAeEAM&quot;,&quot;FlsrUid&quot;:&quot;hjow5L3YcntZsnNuEd5n&quot;,&quot;SourceType&quot;:&quot;Field&quot;,&quot;SourceFieldName&quot;:&quot;IsAssetizable&quot;,&quot;SourceContextTag&quot;:&quot;IsAssetizable&quot;,&quot;TargetType&quot;:&quot;Attribute&quot;,&quot;TargetAttributeId&quot;:&quot;0tjxx000000004rAAA&quot;,&quot;CalculationMethod&quot;:&quot;Ad-verbatim&quot;,&quot;ExecutionStatus&quot;:&quot;SUCCESS&quot;},{&quot;EnrichmentRuleId&quot;:&quot;13Txx0000004CKKEA2&quot;,&quot;DecompRuleId&quot;:&quot;13Uxx0000004CAeEAM&quot;,&quot;FlsrUid&quot;:&quot;hjow5L3YcntZsnNuEd5n&quot;,&quot;SourceType&quot;:&quot;Field&quot;,&quot;SourceFieldName&quot;:&quot;PricebookEntryId&quot;,&quot;SourceContextTag&quot;:&quot;ItemPricebookEntry&quot;,&quot;TargetType&quot;:&quot;Attribute&quot;,&quot;TargetAttributeId&quot;:&quot;0tjxx000000003FAAQ&quot;,&quot;CalculationMethod&quot;:&quot;Ad-verbatim&quot;,&quot;ExecutionStatus&quot;:&quot;SUCCESS&quot;}],&quot;OrderId&quot;:&quot;801xx000003GZSxAAO&quot;,&quot;SubmitMode&quot;:&quot;Synchronous&quot;,&quot;UniqueRequestId&quot;:&quot;5dd3888e-e883-4770-b0ad-aa59e88450eb&quot;,&quot;ContextId&quot;:&quot;d9995de15eea0b3c1ed0a552813fe9cd02b73d0de80c0c15fd4e8ac6661508df&quot;,&quot;DesActionSpecDevName&quot;:&quot;DroDecompEnrichmentAction&quot;,&quot;ContextDefinition&quot;:&quot;SalesTransactionContext__stdctx&quot;}",
          "additionalFilter": "undef",
          "applicationLogDate": "Tue May 07 13:05:28 GMT 2024",
          "applicationSubtype": "DroDcmp",
          "applicationType": "7",
          "explainabilitySpecName": "DroDecompEnrichmentAction",
          "isChunked": false,
          "name": "DroDecompEnrichmentAction",
          "primaryFilter": "801xx000003GZSxAAO",
          "processType": "DcmpEnrich",
          "secondaryFilter": "hjow5L3YcntZsnNuEd5n",
          "uniqueIdentifier": "7ce652e3-81a0-4b2d-a072-88b012c83864"
        },
        {
          "actionContextCode": "801xx000003GZSxAAO",
          "actionLog": "{&quot;CandidateDecompositionRules&quot;:[{&quot;decompRuleId&quot;:&quot;13Uxx0000004CCGEA2&quot;,&quot;SourceProductId&quot;:&quot;01txx0000006i5gAAA&quot;,&quot;AssociatedOlis&quot;:[&quot;802xx000001nbKhAAI&quot;],&quot;DestinationProductId&quot;:&quot;01txx0000006iAWAAY&quot;,&quot;DestinationProductScope&quot;:&quot;OrderLineItem&quot;,&quot;ConfiguredContextRuleId&quot;:&quot;null&quot;},{&quot;decompRuleId&quot;:&quot;13Uxx0000004CAeEAM&quot;,&quot;SourceProductId&quot;:&quot;01txx0000006i5gAAA&quot;,&quot;AssociatedOlis&quot;:[&quot;802xx000001nbKhAAI&quot;],&quot;DestinationProductId&quot;:&quot;01txx0000006i8uAAA&quot;,&quot;DestinationProductScope&quot;:&quot;OrderLineItem&quot;,&quot;ConfiguredContextRuleId&quot;:&quot;null&quot;}],&quot;SelectedDecompositionRules&quot;:[{&quot;OliId&quot;:&quot;802xx000001nbKhAAI&quot;,&quot;DecompositionRuleIds&quot;:[&quot;13Uxx0000004CCGEA2&quot;,&quot;13Uxx0000004CAeEAM&quot;]}],&quot;OliScopeDetails&quot;:[],&quot;FoliComputationDetails&quot;:[{&quot;FoliId&quot;:&quot;0a4xx00000000ODAAY&quot;,&quot;ComputedAction&quot;:&quot;ADD&quot;,&quot;ComputedQuantity&quot;:&quot;1.0&quot;},{&quot;FoliId&quot;:&quot;0a4xx00000000OEAAY&quot;,&quot;ComputedAction&quot;:&quot;ADD&quot;,&quot;ComputedQuantity&quot;:&quot;1.0&quot;}],&quot;FlsrDetails&quot;:[{&quot;FlsrId&quot;:&quot;16Axx0000004CXEEA2&quot;,&quot;FlsrGuid&quot;:&quot;qrh0Z3xv6buew1BW0wdn&quot;,&quot;SourceId&quot;:&quot;802xx000001nbKhAAI&quot;,&quot;FoliId&quot;:&quot;0a4xx00000000ODAAY&quot;},{&quot;FlsrId&quot;:&quot;16Axx0000004CXFEA2&quot;,&quot;FlsrGuid&quot;:&quot;hjow5L3YcntZsnNuEd5n&quot;,&quot;SourceId&quot;:&quot;802xx000001nbKhAAI&quot;,&quot;FoliId&quot;:&quot;0a4xx00000000OEAAY&quot;}],&quot;OrderId&quot;:&quot;801xx000003GZSxAAO&quot;,&quot;SubmitMode&quot;:&quot;Synchronous&quot;,&quot;UniqueRequestId&quot;:&quot;5dd3888e-e883-4770-b0ad-aa59e88450eb&quot;,&quot;ContextId&quot;:&quot;c132f6fca3628bf9608c0e61865b4cd0d9de1479f5171686abc040c69f0504d7&quot;,&quot;DesActionSpecDevName&quot;:&quot;DroDecompScopeAction&quot;,&quot;ContextDefinition&quot;:&quot;SalesTransactionContext__stdctx&quot;}",
          "additionalFilter": "undef",
          "applicationLogDate": "Tue May 07 13:05:32 GMT 2024",
          "applicationSubtype": "DroDcmp",
          "applicationType": "7",
          "explainabilitySpecName": "DroDecompScopeAction",
          "isChunked": false,
          "name": "DroDecompScopeAction",
          "primaryFilter": "801xx000003GZSxAAO",
          "processType": "DcmpScp",
          "secondaryFilter": "undef",
          "uniqueIdentifier": "9f633a63-67d0-4f90-b4dc-c368defe8b44"
        },
        {
          "actionContextCode": "801xx000003GZSxAAO",
          "actionLog": "{&quot;CandidateProductFulfillmentScenarios&quot;:[{&quot;ProductFulfillmentScenarioId&quot;:&quot;1axxx0000000001AAA&quot;,&quot;ProductId&quot;:&quot;01txx0000006i8uAAA&quot;,&quot;FulfillmentStepDefinitionGroupId&quot;:&quot;13oxx0000004CFUAA2&quot;,&quot;LineItemIds&quot;:[&quot;0a4xx00000000OEAAY&quot;]},{&quot;ProductFulfillmentScenarioId&quot;:&quot;1axxx0000000002AAA&quot;,&quot;ProductId&quot;:&quot;01txx0000006i8uAAA&quot;,&quot;FulfillmentStepDefinitionGroupId&quot;:&quot;13oxx0000004CH6AAM&quot;,&quot;LineItemIds&quot;:[&quot;0a4xx00000000OEAAY&quot;]}],&quot;SelectedProductFulfillmentScenarios&quot;:[&quot;1axxx0000000001AAA&quot;,&quot;1axxx0000000002AAA&quot;],&quot;SelectedProductFulfillmentScenariosByOli&quot;:[{&quot;OliId&quot;:&quot;802xx000001nbKhAAI&quot;,&quot;ProductFulfillmentScenarios&quot;:[]},{&quot;OliId&quot;:&quot;0a4xx00000000ODAAY&quot;,&quot;ProductFulfillmentScenarios&quot;:[]},{&quot;OliId&quot;:&quot;0a4xx00000000OEAAY&quot;,&quot;ProductFulfillmentScenarios&quot;:[&quot;1axxx0000000001AAA&quot;,&quot;1axxx0000000002AAA&quot;]}],&quot;PlanId&quot;:&quot;13Vxx0000004Ck8EAE&quot;,&quot;FulfillmentStepCreationStatus&quot;:&quot;FulfillmentStepsCreated&quot;,&quot;FulfillmentStepDependencyCreationStatus&quot;:&quot;FulfilmentStepDepCreated&quot;,&quot;OrderId&quot;:&quot;801xx000003GZSxAAO&quot;,&quot;SubmitMode&quot;:&quot;Synchronous&quot;,&quot;UniqueRequestId&quot;:&quot;5dd3888e-e883-4770-b0ad-aa59e88450eb&quot;,&quot;ContextId&quot;:&quot;c132f6fca3628bf9608c0e61865b4cd0d9de1479f5171686abc040c69f0504d7&quot;,&quot;DesActionSpecDevName&quot;:&quot;DroPlanCompStepsAction&quot;,&quot;ContextDefinition&quot;:&quot;SalesTransactionContext__stdctx&quot;}",
          "additionalFilter": "undef",
          "applicationLogDate": "Tue May 07 13:05:33 GMT 2024",
          "applicationSubtype": "DroPcmp",
          "applicationType": "7",
          "explainabilitySpecName": "DroPlanCompStepsAction",
          "isChunked": false,
          "name": "DroPlanCompStepsAction",
          "primaryFilter": "801xx000003GZSxAAO",
          "processType": "PcmpSteps",
          "secondaryFilter": "undef",
          "uniqueIdentifier": "47a956a6-ae52-4e4a-843b-08b404beb52a"
        },
        {
          "actionContextCode": "801xx000003GZSxAAO",
          "actionLog": "{&quot;OrderId&quot;:&quot;801xx000003GZSxAAO&quot;,&quot;SubmitMode&quot;:&quot;Synchronous&quot;,&quot;UniqueRequestId&quot;:&quot;5dd3888e-e883-4770-b0ad-aa59e88450eb&quot;,&quot;ContextId&quot;:&quot;c132f6fca3628bf9608c0e61865b4cd0d9de1479f5171686abc040c69f0504d7&quot;,&quot;DesActionSpecDevName&quot;:&quot;DroSubmitAction&quot;,&quot;ContextDefinition&quot;:&quot;SalesTransactionContext__stdctx&quot;}",
          "additionalFilter": "undef",
          "applicationLogDate": "Tue May 07 13:06:30 GMT 2024",
          "applicationSubtype": "DroSubmit",
          "applicationType": "7",
          "explainabilitySpecName": "DroSubmitAction",
          "isChunked": false,
          "name": "DroSubmitAction",
          "primaryFilter": "801xx000003GZSxAAO",
          "processType": "DroSubmit",
          "secondaryFilter": "undef",
          "uniqueIdentifier": "278caec4-680c-4df8-a1b2-608e05e44baa"
        }
      ],
      "queryMore": ""
    }
    ```
