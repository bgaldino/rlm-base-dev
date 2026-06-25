---
page_id: actions_obj_expression_set.htm
title: Expression Set Actions
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/actions_obj_expression_set.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_invocable_actions.htm
fetched_at: 2026-06-25
---

# Expression Set Actions

Invoke an active expression set. An expression set is a user-defined
rule that accepts an input and returns the output based on the configured
function.

The configured function of an expression set can be a simple decision matrix lookup, a
calculation based on a mathematical formula, a condition, or another expression set.

When a Flow is invoked using Batch management (for example, for processing 200 records),
the calls to expression sets are automatically bulkified, which allows the execution of
multiple inputs in a single request.

These actions are available in API version 55.0 and later.

## Supported REST HTTP Methods

URI
:   `/services/data/v55.0/actions/custom/runExpressionSet/{ApiName}`

    ![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

    #### Note

    The
    API name of an expression set is unique within your Salesforce instance.

Formats
:   JSON

HTTP Methods
:   POST

Authentication
:   `Authorization: Bearer
    token`

## Inputs

Inputs vary depending on the selected expression set. For expression sets tied to a context
definition, you can build and persist context data using additional inputs.

| Input | Details |
| --- | --- |
| \_\_<ContextNode>​RecordIds | Type  List<String>  Description  Optional. A collection of context node record IDs to be built. |
| \_\_mappingName | Type  String  Description  Optional. The default context mapping available in the context definition. |
| \_\_persist​ContextData | Type  Boolean  Description  Optional. Indicates whether to save context data to the database (`true`) or not (`false`). |
| \_\_buildContext | Type  String  Description  Optional. Indicates whether to build the context using the IDs of context definition records in the database. |

For context-based expression sets, provide either the context ID or the build context
parameters. If both are provided and `__buildContext` is
`true`, the context ID is ignored and the context is
built from the input record IDs.

## Outputs

Vary depending on the inputs of the selected expression set.

## Usage

When the expression set is not linked with a context
:   This section has the sample request and response for invoking an expression set with
    these steps.

    1. Find the tax percentage and the premium corresponding to specific age and salary
       using a decision matrix lookup.
    2. Check the age criterion to calculate the total tax.
    3. Calculate the total tax to be paid based on the age group, salary, and the tax
       percentage.

    Sample request
    :   Here’s an example POST request that has the inputs, such as, age and
        salary.

        ```
        {
          "inputs": [
            {
              "Age": "25.00",
              "Salary": "50000.00"
            },
            {
              "Age": "30.00",
              "Salary": "70000.00"
            },
            {
              "Age": "40.00",
              "Salary": "90000.00"
            }
          ]
        }
        ```

    Sample response
    :   Here’s an example response that has the premium and tax values based on the
        inputs provided in the example request.

        ```
        [
          {
            "actionName": "TaxPremiumES",
            "errors": null,
            "isSuccess": true,
            "outputValues": {
              "TaxPremium__Premium": 1000,
              "TaxPremium__Tax": 10,
              "TaxToBePaid": 1050,
              "condition_output__2": "false",
              "condition_output__1": "true"
            }
          },
          {
            "actionName": "TaxPremiumES",
            "errors": null,
            "isSuccess": true,
            "outputValues": {
              "TaxPremium__Premium": 1500,
              "TaxPremium__Tax": 12,
              "TaxToBePaid": 1512,
              "condition_output__2": "true",
              "condition_output__1": "false"
            }
          },
          {
            "actionName": "TaxPremiumES",
            "errors": null,
            "isSuccess": true,
            "outputValues": {
              "TaxPremium__Premium": 2000,
              "TaxPremium__Tax": 15,
              "TaxToBePaid": 2015,
              "condition_output__2": "false",
              "condition_output__1": "true"
            }
          }
        ]
        ```

When the expression set is linked with a context
:   An expression set can be configured with a context definition. In this case, the
    expression set runs using context data that is either provided directly or built at
    runtime.

    Sample request when context ID is available
    :   Here's an example request that runs a context-based expression set using an
        existing context ID.

        ```
        {
          "inputs": [
            {
              "Claim2Id": "55304396580d20ffbae5111a641ab0a747ffbe47dfab2b16df35df9ac87184fc",
              "inputVar1": 10
            }
          ]
        }
        ```

    Sample response
    :   Here's an example response for a context-based expression set execution.

        ```
        [
          {
            "actionName": "ClaimProcessingES",
            "errors": null,
            "isSuccess": true,
            "outputValues": {
              "Claim2Id": "55304396580d20ffbae5111a641ab0a747ffbe47dfab2b16df35df9ac87184fc",
              "inputVar1": 10
            }
          }
        ]
        ```

    Sample request when context ID is not available
    :   When an expression set is tied to a context definition and a context ID isn't
        available, use the `__buildContext` parameter
        to build the context before the expression set runs. You can also persist the
        context data to the database after execution by setting `__persistContextData` to `true`.

        Here's an example POST request that builds the context, runs the expression
        set, and persists the context data.

        ```
        {
          "inputs": [
            {
              "inputVar1": 10,
              "__buildContext": true,
              "__StudentRecordIds": ["a02xx000001nf9nAAA"],
              "__mappingName": "Default Mapping",
              "__persistContextData": true
            }
          ]
        }
        ```

    Sample response
    :   Here's an example response that includes the context ID that was built during
        execution.

        ```
        [
          {
            "actionName": "StudentEligibilityES",
            "errors": null,
            "isSuccess": true,
            "outputValues": {
              "StudentId": "55304396580d20ffbae5111a641ab0a747ffbe47dfab2b16df35df9ac87184fc",
              "inputVar1": 10
            }
          }
        ]
        ```
