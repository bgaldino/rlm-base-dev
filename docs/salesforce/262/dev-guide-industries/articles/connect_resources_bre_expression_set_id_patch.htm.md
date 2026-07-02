---
page_id: connect_resources_bre_expression_set_id_patch.htm
title: Expression Set (PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_expression_set_id_patch.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_resources.htm
fetched_at: 2026-06-25
---

# Expression Set (PATCH)

Endpoint to update expression set.

Resource
:   ```
    /connect/business-rules/expression-set/${expressionSetId}
    ```

Resource Example
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/business-rules/expression-set/$11Oxx0000006PcLEAU
    ```

Available version
:   58.0

Requires Chatter
:   No

HTTP methods
:   PATCH

Request body for PATCH
:   Root XML tag
    :   `<ExpressionSetInput>`

    JSON example
    :   ```
        {
          "name": "CTX Mapping ES",
          "apiName": "CTX_Mapping_ES_1",
          "description": "...",
          "usageType": "Bre",
          "contextDefinitions": [
            {
              "id": "11Oxx0000006PcLEAU"
            }
          ],
          "versions": [
            {
              "name": "CTX_Mapping_ES_1 V1",
              "apiName": "CTX_Mapping_ES_1_V1",
              "description": "Sample CTX Mapping",
              "startDate": "2022-11-14T20:31:47.000+0000",
              "endDate": "2022-11-14T20:31:47.000+0000",
              "versionNumber": 1,
              "rank": 1,
              "enabled": true,
              "showExplExternally": false,
              "steps": [
                {
                  "name": "Condition1",
                  "description": "Condition step for conditions w.r.t product",
                  "sequenceNumber": 1,
                  "resultIncluded": true,
                  "stepType": "Condition",
                  "conditionExpression": {
                    "expression": "productName == 'iPhone' && productColor == 'Red'",
                    "resultParameter": "condition_output__1"
                  }
                }
              ],
              "variables": [
                {
                  "name": "productName",
                  "collection": false,
                  "dataType": "Text",
                  "description": "productName",
                  "input": true,
                  "output": false,
                  "type": "Variable"
                },
                {
                  "name": "productColor",
                  "collection": false,
                  "dataType": "Text",
                  "description": "productColor",
                  "input": true,
                  "output": false,
                  "type": "Variable"
                },
                {
                  "name": "condition_output__1",
                  "dataType": "Boolean",
                  "description": "condition_output__1",
                  "input": false,
                  "output": true,
                  "resultStep": "Condition1",
                  "type": "Variable"
                }
              ]
            }
          ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `apiName` | String | Unique name of the expression set. | Required | 58.0 |
        | `context​Definitions` | [Context Definition Input](./connect_requests_context_definition_input.htm.md "Input representation of the context definitions in an expression set.") | List of context definitions in an expression set. | Optional | 58.0 |
        | `description` | String | Description of the expression set. | Optional | 58.0 |
        | `name` | String | Name of the expression set. | Required | 58.0 |
        | `usage​Type` | String | Usage type of the expression set. Valid value is `Bre`. The default value is `Bre`.  When Business Rules Engine is enabled for a Salesforce org, the default value is `Bre`. Other usage types may be available to you depending on your industry solution and permission sets. | Required | 58.0 |
        | `versions` | [Expression Set Version Input](./connect_requests_expression_set_version.htm.md "Input representation of an expression set version.")[] | List of the expression set versions. | Optional | 58.0 |

Response body for PATCH
:   [Expression Set Output](./connect_responses_expression_set_output.htm.md "Output representation of the expression set create, update and delete request.")
