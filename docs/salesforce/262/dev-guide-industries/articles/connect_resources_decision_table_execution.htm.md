---
page_id: connect_resources_decision_table_execution.htm
title: Decision Table Execution
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_decision_table_execution.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apis_resources.htm
fetched_at: 2026-06-25
---

# Decision Table Execution

Execute an active decision table.

Resource
:   ```
    services/data/vXX.X/connect/business-rules/decision-table/lookup/${decisionTableId}
    ```

Available version
:   51.0

Requires Chatter
:   No

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
           "conditions":[
              {
                 "conditionsList":[
                    {
                       "fieldName":"Product__c",
                       "value":"Nike",
                       "operator":"Matches"
                    },
                    {
                       "fieldName":"Price__c",
                       "value":1000,
                       "operator":"GreaterThan"
                    }
                 ]
              },
              {
                 "conditionsList":[
                    {
                       "fieldName":"Product__c",
                       "value":"Adidas",
                       "operator":"Matches"
                    },
                    {
                       "fieldName":"Price__c",
                       "value":1500,
                       "operator":"GreaterThan"
                    }
                 ]
              }
           ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `conditions` | [Decision Table Condition](./connect_requests_decision_table_condition.htm.md "Input representation of the decision table condition.")[] | The list of decision table conditions on which the decision table executes and provides outcomes. | Required | 55.0 |
        | `datasetLinkName` | String | The API name of the dataset link provided as an input for the decision table execution. | Optional | 55.0 |

Response body for POST
:   [Decision Table Outcome](./connect_responses_decision_table_outcome.htm.md "Output representation of the decision table execution.")

Sample Response body
:   ```
    {
       “outcomeType” : “Single Match”,
       "outcomeList" : [
          {
             “values” : {
                “Discount_c”: 5
             }
          }
       ]
    }
    ```
