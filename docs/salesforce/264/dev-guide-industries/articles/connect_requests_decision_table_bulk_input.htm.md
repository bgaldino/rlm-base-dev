---
page_id: connect_requests_decision_table_bulk_input.htm
title: Decision Table Bulk Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_decision_table_bulk_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Table Bulk Input

Input representation of the Decision Table bulk
      lookup.

      
         
            
               

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
