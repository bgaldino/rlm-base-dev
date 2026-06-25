---
page_id: connect_resources_bre_decision_table.htm
title: Decision Table Lookup (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_decision_table.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_table_resources.htm
fetched_at: 2026-06-25
---

# Decision Table Lookup (POST)

Performs a lookup on a decision table.

Resource
:   ```
    /connect/business-rules/decision-table/${decisionTableId}
    ```

Resource Example
:   ```
    https://yourInstance.salesforce.com/services/data/v55.0/connect
    /decision-table/0lDB0000000TNQzMAO
    ```

Available version
:   55.0

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
