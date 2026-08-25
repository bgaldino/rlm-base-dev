---
page_id: apex_ConnectAPI_DecisionTable_execute_1.htm
title: execute(decisionTableId, DecisionTableInput)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/apex_ConnectAPI_DecisionTable_execute_1.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apex_methods.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

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

      
      
        
          

**decisionTableId**

          
: Type: String

          
: ID of the decision table.

        
        
          

**DecisionTableInput**

          
: Type: [`ConnectApi.DecisionTableInput`](./apex_connectapi_input_decision_table.htm.md)

          
: A `ConnectApi.DecisionTableInput` object with a
            list of conditions.

        
      

    

    

## Return Value

      
      

Type: [`ConnectApi.DecisionTableOutcome`](./apex_connectapi_output_decision_table_outcome.htm.md)

    

    

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
