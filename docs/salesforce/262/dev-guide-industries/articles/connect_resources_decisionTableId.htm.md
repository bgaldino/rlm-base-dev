---
page_id: connect_resources_decisionTableId.htm
title: Decision Table Invocation (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_decisionTableId.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_table_resources.htm
fetched_at: 2026-06-25
---

# Decision Table Invocation (POST)

Invoke a decision table by passing multiple input conditions within
the same request.

Resource
:   ```
    /connect/business-rules/decision-table/lookup/${decisionTableId}
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect
    /business-rules/decision-table/lookup/${0lDD2000000004NMAQ}
    ```

Available version
:   58.0

Requires Chatter
:   No

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
           "datasetLinkName" : "transactionMapping",
           “conditions” :[
              {
                “conditionsList”: [
                  {
                      "fieldName": "Product__c",
                      "value": "Nike",
                      "operator": "Matches" //Operator is optional
                  },
                  {
                      "fieldName": "Price__c",
                      "value": 1000,
                      "operator": "GreaterThan"
                  }
                ]
              },
              {
                “conditionsList”: [
                  {
                      "fieldName": "Product__c",
                      "value": "Adidas",
                      "operator": "Matches" //Operator is optional
                  },
                  {
                      "fieldName": "Price__c",
                      "value": 1500,
                      "operator": "GreaterThan"
                  }
                ]
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `conditions` | [Decision Table Condition List](./connect_requests_decision_table_condition_list_input.htm.md "Input representation of the Decision Table condition list.") | The list of decision table conditions on which the decision table executes and provides outcomes. | Required | 58.0 |
        | `datasetLinkName` | String | The API name of the dataset link provided as an input for the decision table execution. | Optional | 58.0 |

Response body for POST
:   [Decision Table Bulk Outcome](./connect_responses_decision_table_bulk_outcome.htm.md "Output representation of the decision table bulk look-up.")
