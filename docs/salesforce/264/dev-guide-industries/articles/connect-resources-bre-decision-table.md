---
page_id: connect-resources-bre-decision-table
title: Decision Table Lookup (POST)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-bre-decision-table.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: lookup-table-resources
legacy_page_id: connect_resources_bre_decision_table.htm
fetched_at: 2026-11-25
---

# Decision Table Lookup (POST)

Performs a lookup on a decision table.

## Resource

```
/connect/business-rules/decision-table/${decisionTableId}
```

The {decisionTableId} parameter is the ID of the decision table.

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v55.0/connect
/decision-table/0lDB0000000TNQzMAO
```

{yourInstance} is the domain name of your Salesforce instance.

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
| `conditions` | [Decision Table Condition](./connect-requests-decision-table-condition.md)[] | The list of decision table conditions on which the decision table executes and provides outcomes. | Required | 55.0 |
| `datasetLinkName` | String | The API name of the dataset link provided as an input for the decision table execution. | Optional | 55.0 |

## Response Body for POST

[Decision Table Outcome](./connect-responses-decision-table-outcome.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-bre-decision-table.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
