---
page_id: connect_resources_get_create_action_logs.htm
title: Action Logs (GET, POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_get_create_action_logs.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Decision Explainer
parent_page: decision_explainer_apis_resources.htm
fetched_at: 2026-06-25
---

# Action Logs (GET, POST)

Retrieve a paginated list of Explainability action logs. Create an
Explainability action log.

Resource
:   ```
    /connect/decision-explainer/action-logs
    ```

Example for GET
:   ```
    https://yourInstance.salesforce.com/services/data/vXX.X/connect​​/
    decision-explainer/action-logs?actionContextCode=001x0000005DmI3AAK
    ```

Example for POST
:   ```
    https://yourInstance.salesforce.com/services/data/vXX.X/connect​​/
    decision-explainer/action-logs
    ```

Available version
:   54.0

Requires Chatter
:   No

HTTP methods
:   GET, POST

Query parameters for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `actionContextCode` | String | The record ID within the context of the associated application's action that’s used to retrieve action logs. | Required | 54.0 |
    | `applicationSubType` | String | The subtype of the associated application for which the explainability log is generated. This matches one of the valid values in the ExplainabilityActionDef `ApplicationSubtype` field. | Optional | 54.0 |
    | `applicationType` | String | The name of the application for which the explainability service is run. This matches one of the valid values in the ExplainabilityActionDef `ApplicationType` field. | Optional | 54.0 |
    | `createdAfter` | String | A valid date time after which the explainability action log records are returned. | Optional | 54.0 |
    | `createdBefore` | String | A valid date time before which the explainability action log records are returned. | Optional | 54.0 |
    | `pageSize` | Integer | The number of explainability action log records to return. The value can range from 200 to 500. | Optional | 54.0 |
    | `processType` | String | The process type of the associated application for which the explainability action log is generated. This matches one of the valid values in the ExplainabilityActionDef `ProcessType` field. | Optional | 54.0 |
    | `queryMore` | String | A string returned from the previous request, which you must pass to the next request to get the next page. | Optional | 54.0 |

Response body for GET
:   [Explainability Action Logs](./connect_responses_explainability_action_logs.htm.md "Output representation of the list of Explainability action logs.")

Request body for POST
:   Root XML tag
    :   `ExplainabilityActionLog`

    JSON example
    :   ```
        {
        "specificationName" : "EAD1",
        "name" : "testEAL1",
        "actionLog" : "{\"input\":{\"input\":{\"input\":2}},\"ruledefinition\":{\"calculationProcedureId\":\"0k0xx00000000JNAAY\",
        \"variables\":{\"details\":[{\"apiName\":\"total\",\"isEditable\":true,\"defaultValue\":null,\"displayName\":null,\"dataType\"
        :\"Number\",\"precision\":2,\"calculationMatrixName\":null,\"name\":\"total\",\"isUserDefined\":true,\"uiDisplayOrder\":null,
        \"id\":\"0kJxx000000018zEAA\"},{\"apiName\":\"input\",\"isEditable\":true,\"defaultValue\":\"10\",\"displayName\":null,\"dataType\"
        :\"Number\",\"precision\":2,\"calculationMatrixName\":null,\"name\":\"input\",\"isUserDefined\":true,\"uiDisplayOrder\":null,\"id\"
        :\"0kJxx00000001AbEAI\"}]},\"code\":null,\"endDate\":null,\"description\":null,\"message\":null,\"enabled\":true,\"versionNumber\":2,
        \"versionId\":\"0k1xx00000000knAAA\",\"root\":{\"steps\":[\"0mqxx00000001TxAAI\"]},\"name\":\"es1 V1 CLONE\",\"rank\":2,\"step\":
        {\"details\":{\"0mqxx00000001TxAAI\":{\"inputVariablesFormatText\":\"[{\\\"name\\\":\\\"input\\\",\\\"dataType\\\":\\\"Number\\\",
        \\\"alias\\\":\\\"input\\\"}]\",\"stepType\":\"Calculation\",\"outputVariablesFormatText\":\"{\\\"name\\\":\\\"total\\\",\\\"dataType\\\":
        \\\"Number\\\",\\\"alias\\\":\\\"total\\\"}\",\"conditionsUiFormattedText\":\"{\\\"bypass\\\":{},\\\"stepNumber\\\":3}\",
        \"formulaUiFormattedText\":null,\"description\":null,\"outputVariablesMappingText\":\"{\\\"total\\\":\\\"total\\\"}\",
        \"conditionsExpressionText\":null,\"calculationMatrixId\":null,\"isResultIncluded\":true,\"formulaExpressionText\":\"10 * input\",\"stage\":
        \"Calculation\",\"name\":\"Calculation\",\"childStepIds\":[],\"referenceCalculationProcedureId\":null,\"id\":\"0mqxx00000001TxAAI\",
        \"returnMessageValueSet\":\"{\\\"true\\\":\\\"\\\",\\\"false\\\":\\\"\\\"}\"}}},\"constants\":{\"details\":[]},\"startDate\":1637684784000,
        \"isSuccess\":null},\"runtime\":{\"output\":[{\"aggregationResults\":{},\"calculationResults\":[{\"total\":20,\"ID\":\"input\"}]}],\"simulate\"
        :{\"0mqxx00000001TxAAI\":{\"stepInputs\":{\"input\":2},\"stepResults\":{\"total\":20}}}}}",
        "actionLogDate" : "2021-09-15T03:18:30.081Z",
        "actionContextCode" : "0f0xx0000000001AAA"
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `action​Context​Code` | String | The valid Salesforce record ID that’s used to retrieve the explainability action logs. | Required | 54.0 |
        | `actionLog` | String | The contents of the explainability action log. | Required | 54.0 |
        | `action​LogDate` | String | The date and time when the explainability action log was generated by the application’s action. | Required | 54.0 |
        | `actionLog​OwnerId` | String | The ID of the user who owns the action log. | No | 54.0 |
        | `additional​Filter` | String | The string that’s used as an additional filter criteria to fetch the explainability action logs. | Optional | 57.0 |
        | `name` | String | A name to identify the explainability action log record. | No | 54.0 |
        | `primary​Filter` | String | The string that’s used as the primary filter criteria to fetch the explainability action logs. | Optional | 57.0 |
        | `secondary​Filter` | String | The string that’s used as the secondary filter criteria to fetch the explainability action logs. | Optional | 57.0 |
        | `specification​Name` | String | A unique name that identifies an active explainability action log record. | Required | 54.0 |

Response body for POST
:   [Explainability Action Log Create](./connect_responses_explainability_action_log_create.htm.md "Output representation of the create Explainability action log request.")
