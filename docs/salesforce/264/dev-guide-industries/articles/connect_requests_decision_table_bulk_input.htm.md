---
page_id: connect_requests_decision_table_bulk_input.htm
title: Decision Table Bulk Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_decision_table_bulk_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_requests.htm
fetched_at: 2026-11-23
---

# Decision Table Bulk Input

Input representation of the Decision Table bulk
lookup.

## JSON Example

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

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `conditions` | [Decision Table Condition List](./connect_requests_decision_table_condition_list_input.htm.md "Input representation of the Decision Table condition list.") | The list of decision table conditions on which the decision table executes and provides outcomes. | Required | 58.0 |
| `datasetLinkName` | String | The API name of the dataset link provided as an input for the decision table execution. | Optional | 58.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_decision_table_bulk_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
