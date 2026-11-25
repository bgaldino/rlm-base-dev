---
page_id: connect-resources-decision-table-execution
title: Decision Table Execution
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-decision-table-execution.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: decision-table-apis-resources
legacy_page_id: connect_resources_decision_table_execution.htm
fetched_at: 2026-11-25
---

# Decision Table Execution

Execute an active decision table.

## Resource

```
services/data/vXX.X/connect/business-rules/decision-table/lookup/${decisionTableId}
```

## Available Version

51.0

## Requires Chatter

No

## HTTP Methods

POST

## Sample Response body

```
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

## Request Body for POST

### JSON Example

```
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

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `conditions` | [Decision Table Condition](./connect-requests-decision-table-condition.md)[] | The list of decision table conditions on which the decision table executes and provides outcomes. | Required | 55.0 |
| `datasetLinkName` | String | The API name of the dataset link provided as an input for the decision table execution. | Optional | 55.0 |

## Response Body for POST

[Decision Table Outcome](./connect-responses-decision-table-outcome.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-decision-table-execution.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
