---
page_id: connect_resources_bre_decision_table.htm
title: Decision Table Lookup (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_decision_table.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_table_resources.htm
fetched_at: 2026-11-23
---

# Decision Table Lookup (POST)

Performs a lookup on a decision table.

## Resource

```
/connect/business-rules/decision-table/${decisionTableId}
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v55.0/connect
/decision-table/0lDB0000000TNQzMAO
```

## Available Version

55.0

## Requires Chatter

No

## HTTP Methods

POST

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
| `conditions` | [Decision Table Condition](./connect_requests_decision_table_condition.htm.md "Input representation of the decision table condition.")[] | The list of decision table conditions on which the decision table executes and provides outcomes. | Required | 55.0 |
| `datasetLinkName` | String | The API name of the dataset link provided as an input for the decision table execution. | Optional | 55.0 |

## Response Body for POST

[Decision Table Outcome](./connect_responses_decision_table_outcome.htm.md "Output representation of the decision table execution.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_decision_table.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
