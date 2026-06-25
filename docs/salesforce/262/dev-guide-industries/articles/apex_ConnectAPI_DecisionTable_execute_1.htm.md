---
page_id: apex_ConnectAPI_DecisionTable_execute_1.htm
title: execute(decisionTableId, DecisionTableInput)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/apex_ConnectAPI_DecisionTable_execute_1.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apex_methods.htm
fetched_at: 2026-06-25
---

# execute(decisionTableId, DecisionTableInput)

Execute an active decision table.

## API Version

51.0

## Requires Chatter

No

## Signature

`public static ConnectApi.DecisionTableOutcome execute(String
decisionTableId, ConnectApi.DecisionTableInput DecisionTableInput)`

## Parameters

decisionTableId
:   Type: String
:   ID of the decision table.

DecisionTableInput
:   Type: [`ConnectApi.DecisionTableInput`](./apex_connectapi_input_decision_table.htm.md "Input representation of the decision table.")
:   A `ConnectApi.DecisionTableInput` object with a
    list of conditions.

## Return Value

Type: [`ConnectApi.DecisionTableOutcome`](./apex_connectapi_output_decision_table_outcome.htm.md "Output representation of the decision table execution.")

## Example

```
ConnectApi.DecisionTableInput input = new ConnectApi.DecisionTableInput();
input.datasetLinkName = ‘DSL1’;//Optional,if you want to use a dataset link mapping definition
input.conditions = new List<ConnectApi.DecisionTableCondition>();
ConnectApi.DecisionTableCondition condition = new ConnectApi.DecisionTableCondition();
condition.fieldName = 'Brand__c';
condition.value = 'Cloud Kicks';
input.conditions.add(condition);
ConnectApi.DecisionTableOutcome output = ConnectApi.DecisionTable.execute('0lDxxxj23444', input);
```
