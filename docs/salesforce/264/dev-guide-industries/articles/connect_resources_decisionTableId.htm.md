---
page_id: connect_resources_decisionTableId.htm
title: Decision Table Invocation (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_decisionTableId.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_table_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Table Invocation (POST)

Invoke a decision table by passing multiple input conditions within
      the same request.

    
      
        
          

**Resource**

          
: 
            

```
/connect/business-rules/decision-table/lookup/${decisionTableId}
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v67.0/connect
/business-rules/decision-table/lookup/${0lDD2000000004NMAQ}
```

          

        
        
          

**Available version**

          
: 58.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
: POST

        
        
          

**Request body for POST**

          
: 
            
            
               

**JSON example**

               
: 
                  

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

               

            
            
               

**Properties**

               
: 
                  

                        
                        
                        
                        
                        
                        
                           
                              

                              

                              

                              

                              

                           

                        

                        
                           
                              

                              

                              

                              

                              

                           

                           
                              

                              

                              

                              

                              

                           

                        

                     
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `conditions` | [Decision Table Condition List](./connect_requests_decision_table_condition_list_input.htm.md) | The list of decision table conditions on which the decision table executes and provides outcomes. | Required | 58.0 |
| `datasetLinkName` | String | The API name of the dataset link provided as an input for the decision table execution. | Optional | 58.0 |

               

            
         

          

        
        
          

**Response body for POST**

          
: [Decision Table Bulk Outcome](./connect_responses_decision_table_bulk_outcome.htm.md)
