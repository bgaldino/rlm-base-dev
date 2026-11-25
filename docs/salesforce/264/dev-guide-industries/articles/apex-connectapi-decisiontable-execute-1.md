---
page_id: apex-connectapi-decisiontable-execute-1
title: execute(decisionTableId, DecisionTableInput)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/apex-connectapi-decisiontable-execute-1.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: decision-table-apex-methods
legacy_page_id: apex_ConnectAPI_DecisionTable_execute_1.htm
fetched_at: 2026-11-25
---

# execute(decisionTableId, DecisionTableInput)

Execute an active decision table.

## API Version

51.0

## Requires Chatter

No

## Signature

`public static ConnectApi.DecisionTableOutcome execute(String decisionTableId, ConnectApi.DecisionTableInput DecisionTableInput)`

## Parameters

***decisionTableId***

: 

Type: [String](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_methods_system_string.htm#apex_methods_system_string)

ID of the decision table.

***DecisionTableInput***

: 

Type: [`ConnectApi.DecisionTableInput`](./apex-connectapi-input-decision-table.md)

A `ConnectApi.DecisionTableInput` object with the lookup conditions. For a versioned CSV decision table, the object can also include lookup options.

## Return Value

Type: [`ConnectApi.DecisionTableOutcome`](./apex-connectapi-output-decision-table-outcome.md)

## Example

```
ConnectApi.DecisionTableInput input = new ConnectApi.DecisionTableInput();
input.datasetLinkName = 'DSL1';
input.conditions = new List<ConnectApi.DecisionTableCondition>();
ConnectApi.DecisionTableCondition condition = new ConnectApi.DecisionTableCondition();
condition.fieldName = 'Brand__c';
condition.value = 'Cloud Kicks';
input.conditions.add(condition);
input.options = new ConnectApi.DecisionTableBulkLookupOptions();
input.options.effectiveDate = '2022-12-03T10:15:30Z';
ConnectApi.DecisionTableOutcome output = ConnectApi.DecisionTable.execute('0lDxxxj23444', input);
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/apex-connectapi-decisiontable-execute-1.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
