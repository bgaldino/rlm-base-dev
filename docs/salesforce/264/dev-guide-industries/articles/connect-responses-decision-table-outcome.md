---
page_id: connect-responses-decision-table-outcome
title: Decision Table Outcome
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-decision-table-outcome.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: decision-table-apis-responses
legacy_page_id: connect_responses_decision_table_outcome.htm
fetched_at: 2026-11-25
---

# Decision Table Outcome

Output representation of the decision table execution.

## JSON Example

```
{
  "errorCode" : null,
  "errorMessage" : null,
  "outcomeList" : [ {
    "values" : {
      "amount__c" : "399",
      "Name" : "MH 005"
    }
  }, {
    "values" : {
      "amount__c" : "499",
      "Name" : "MH 006"
    }
  }, {
    "values" : {
      "amount__c" : "379",
      "Name" : "MH 007"
    }
  }, {
    "values" : {
      "amount__c" : "1498",
      "Name" : "MH 008"
    }
  }, {
    "values" : {
      "amount__c" : "98",
      "Name" : "MH 009"
    }
  }, {
    "values" : {
      "amount__c" : "251",
      "Name" : "MH 010"
    }
  } ],
  "outcomeType" : "Multiple Matches",
  "successStatus" : true
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | Integer | The error code if transaction fails for any reason. | Small, 55.0 | 55.0 |
| `errorMessage` | String | The error message if transaction fails for any reason. | Small, 55.0 | 55.0 |
| `outcomeList` | [Decision Table Outcome Item](./connect-responses-decision-table-outcome-item.md)[] | Outcome list that stores two or more outcomes provided by the decision table. | Small, 55.0 | 55.0 |
| `outcomeType` | String | The outcome type after the request is successful. | Small, 55.0 | 55.0 |
| `successStatus` | Boolean | Indicates the status of the decision table execution. | Small, 55.0 | 55.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-decision-table-outcome.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
