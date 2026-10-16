---
page_id: connect_responses_decision_table_outcome.htm
title: Decision Table Outcome
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_table_outcome.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Table Outcome

Output representation of the decision table
      execution.

      
         
            
               

**JSON example**

               
: 
                  

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

               

            
         

         

               
               
               
               
               
               
                  
                     

                     

                     

                     

                     

                  

               

               
                  
                     

                     

                     

                     

                     

                  

                  
                     

                     

                     

                     

                     

                  

                  
                     

                     

                     

                     

                     

                  

                  
                     

                     

                     

                     

                     

                  

                  
                     

                     

                     

                     

                     

                  

               

            
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | Integer | The error code if transaction fails for any reason. | Small, 55.0 | 55.0 |
| `errorMessage` | String | The error message if transaction fails for any reason. | Small, 55.0 | 55.0 |
| `outcomeList` | [Decision Table Outcome Item](./connect_responses_decision_table_outcome_item.htm.md)[] | Outcome list that stores two or more outcomes provided by the decision table. | Small, 55.0 | 55.0 |
| `outcomeType` | String | The outcome type after the request is successful. | Small, 55.0 | 55.0 |
| `successStatus` | Boolean | Indicates the status of the decision table execution. | Small, 55.0 | 55.0 |
