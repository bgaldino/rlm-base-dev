---
page_id: connect_resources_decisionTableId.htm
title: Decision Table Invocation (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_decisionTableId.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_table_resources.htm
fetched_at: 2026-11-23
---

# Decision Table Invocation (POST)

Invoke a decision table by passing multiple input conditions within
the same request.

## Resource

```
/connect/business-rules/decision-table/lookup/${decisionTableId}
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/connect
/business-rules/decision-table/lookup/${0lDD2000000004NMAQ}
```

## Available Version

58.0

## Requires Chatter

No

## HTTP Methods

POST

## Request Body for POST

### JSON Example

```
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

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `conditions` | [Decision Table Condition List](./connect_requests_decision_table_condition_list_input.htm.md "Input representation of the Decision Table condition list.") | The list of decision table conditions on which the decision table executes and provides outcomes. | Required | 58.0 |
| `datasetLinkName` | String | The API name of the dataset link provided as an input for the decision table execution. | Optional | 58.0 |

## Response Body for POST

[Decision Table Bulk Outcome](./connect_responses_decision_table_bulk_outcome.htm.md "Output representation of the decision table bulk look-up.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_decisionTableId.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
