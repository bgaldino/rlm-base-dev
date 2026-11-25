---
page_id: connect-resources-decisiontableid
title: Decision Table Invocation (POST)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-decisiontableid.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: lookup-table-resources
legacy_page_id: connect_resources_decisionTableId.htm
fetched_at: 2026-11-25
---

# Decision Table Invocation (POST)

Invoke a decision table by passing multiple input conditions within the same request.

## Resource

```
/connect/business-rules/decision-table/lookup/${decisionTableId}
```

The {decisionTableId} parameter is the ID of the decision table.

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect
/business-rules/decision-table/lookup/${0lDD2000000004NMAQ}
```

{yourInstance} is the domain name of your Salesforce instance.

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
  "datasetLinkName": "transactionMapping",
  "conditions": [
    {
      "conditionsList": [
        {
          "fieldName": "Product__c",
          "value": "Nike",
          "operator": "Matches"
        },
        {
          "fieldName": "Price__c",
          "value": 1000,
          "operator": "GreaterThan"
        }
      ]
    },
    {
      "conditionsList": [
        {
          "fieldName": "Product__c",
          "value": "Adidas",
          "operator": "Matches"
        },
        {
          "fieldName": "Price__c",
          "value": 1500,
          "operator": "GreaterThan"
        }
      ]
    }
  ],
  "options": {
    "effectiveDate": "2026-01-15T00:00:00Z"
  }
}
```

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `conditions` | [Decision Table Condition List](./connect-requests-decision-table-condition-list-input.md) | The list of decision table conditions on which the decision table executes and provides outcomes. | Required | 58.0 |
| `datasetLinkName` | String | The API name of the dataset link provided as an input for the decision table execution. | Optional | 58.0 |
| `options` | [Decision Table Bulk Lookup Options](./connect-requests-decision-table-bulk-lookup-options.md) | Lookup options for a versioned CSV decision table. The API ignores these options for any other decision table type. | Optional | 67.0 |

## Response Body for POST

[Decision Table Bulk Outcome](./connect-responses-decision-table-bulk-outcome.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-decisiontableid.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
