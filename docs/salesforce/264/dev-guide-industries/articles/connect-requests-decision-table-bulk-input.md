---
page_id: connect-requests-decision-table-bulk-input
title: Decision Table Bulk Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-decision-table-bulk-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: lookup-tables-requests
legacy_page_id: connect_requests_decision_table_bulk_input.htm
fetched_at: 2026-11-25
---

# Decision Table Bulk Input

Input representation of the Decision Table bulk lookup.

## JSON Example

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

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `conditions` | [Decision Table Condition List](./connect-requests-decision-table-condition-list-input.md) | The list of decision table conditions on which the decision table executes and provides outcomes. | Required | 58.0 |
| `datasetLinkName` | String | The API name of the dataset link provided as an input for the decision table execution. | Optional | 58.0 |
| `options` | [Decision Table Bulk Lookup Options](./connect-requests-decision-table-bulk-lookup-options.md) | Lookup options for a versioned CSV decision table. The API ignores these options for any other decision table type. | Optional | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-decision-table-bulk-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
