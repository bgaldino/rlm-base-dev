---
page_id: actions_obj_run_config_rules.htm
title: Run Config Rules Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_run_config_rules.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Run Config Rules Action

Run rules for a specific quote or order based on a context ID or
transaction ID, and process other steps that are part of the configuration directly
within a Flow. This action decouples rule execution from configurations to enable
independent execution of rules and for easier retrieval of responses.

This action is available in API version 65.0 and later.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/runConfigRules`

Formats
:   JSON, XML

HTTP Methods
:   POST

Authentication
:   `Authorization:
    Bearertoken`

## Inputs

| Input | Details |
| --- | --- |
| transactionContextId | Type  string  Description  Unique identifier for the transaction context. |
| transactionId | Type  string  Description  Required. Unique identifier for the transaction. |

## Outputs

| Output | Details |
| --- | --- |
| configRuleResult | Type  Apex-defined  Description  An `runtime_industries_cpq.ConfigRuleResult` record that contains the configuration rule execution results including validation messages, product recommendations, visibility rules, and errors from rule processing. |
| transactionContextId | Type  string  Description  Unique identifier for the transaction context. |

## Example

POST
:   This example shows a sample request to run rules for the specified quote
    based on the transaction context ID and transaction ID.

    ```
    {
      "inputs": [
        {
          "transactionContextId": "008d27d7-e004-4906-a949-ee7d7c323c77",
          "transactionId": "0Q0DU0000005tJh0AI"
        }
      ]
    }
    ```
:   This example shows a sample successful response.

    ```
    [
      {
        "actionName": "runConfigRules",
        "errors": null,
        "invocationId": null,
        "isSuccess": true,
        "outcome": null,
        "outputValues": {
          "transactionContextId": "0000000p18dq18g0029175793402786243c3d5ea94c241f09c11388ac1b865f9",
          "configRuleResult": {
            "visibilityRules": [
              {
                "stiId": "0QLxx0000004CU0GAM",
                "prcId": "PRC1",
                "attributeId": "Color",
                "attributePicklistValueId": "Red",
                "target": "Attribute",
                "scope": "Product",
                "type": "Hide"
              },
              {
                "stiId": "0QLxx0000004CU0GAM",
                "prcId": "PRC2",
                "attributeId": "Size",
                "attributePicklistValueId": "Large",
                "target": "Attribute",
                "scope": "Bundle",
                "type": "Disable"
              }
            ],
            "transactionContextId": "0000000p18dq18g0029175793402786243c3d5ea94c241f09c11388ac1b865f9",
            "productRecommendationRules": [
              {
                "referenceId": "CORE_BUNDLE_001",
                "productIds": [
                  "01t000000001234",
                  "01t000000005678"
                ]
              }
            ],
            "messageRules": [
              {
                "stiId": "0QLxx0000004CU0GAM",
                "severity": "INFO",
                "messages": [
                  "Product configuration validated successfully"
                ]
              },
              {
                "stiId": "0QLxx0000004CU0GAM",
                "severity": "INFO",
                "messages": [
                  "All required attributes are configured"
                ]
              },
              {
                "stiId": "0QLxx0000004CU0GAM",
                "severity": "INFO",
                "messages": [
                  "Bundle compatibility check passed"
                ]
              }
            ],
            "errors": []
          }
        },
        "sortOrder": -1,
        "version": 1
      }
    ]
    ```
:   Here's a sample input to call this invocable action by using `transactionContextId` property from Apex
    code.

    ```
    // Create the invocable action with namespace
    Invocable.Action action = Invocable.Action.createStandardAction('runConfigRules');
                
    // Set input parameters using setInvocationParameter
    String contextId = '008d27d7-e004-4906-a949-ee7d7c323c77';
    System.debug('Setting transactionContextId parameter with value: ' + contextId);
                
    // Use the exact parameter name format from the debug output
    action.setInvocationParameter('transactionContextId', contextId);
                
    // Debug the action parameters
    System.debug('Action parameters: ' + action);
                
    // Execute the action
    System.debug('Invoking action...');
    List<Invocable.Action.Result> results = action.invoke();
                
    System.debug('Number of results: ' + results.size());
    ```
