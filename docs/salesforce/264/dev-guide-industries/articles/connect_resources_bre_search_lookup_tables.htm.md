---
page_id: connect_resources_bre_search_lookup_tables.htm
title: Lookup Tables (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_search_lookup_tables.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_table_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Lookup Tables (GET)

Retrieve lookup tables.

    
      
        
          

**Resource**

          
: 
            

```
/connect/business-rules/lookup-tables
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v67.0/connect/business-rules/lookup-tables?searchKey=D&usageType=Bre&lookupTypes=DecisionTable,DecisionMatrix
```

          

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v67.0/connect/business-rules/lookup-tables?searchKey=D&usageType=Bre
```

          

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v67.0/connect/business-rules/lookup-tables?searchKey=D&usageType=Bre&lookupTypes=DecisionTable&businessKnowledgeModelName=ManualDiscount
```

          

        
        
          

**Available version**

          
: 59.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
: GET

        
        
          

**Request parameters for GET**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

- 
- 

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `lookupTypes` | String | Type of lookup table. Valid values are: `DecisionMatrix` `DecisionTable` | Optional | 59.0 |
| `searchKey` | String | The search text entered by the user to retrieve a list of lookup tables. | Required | 59.0 |
| `usageType` | String | Usage type of the lookup table. Valid value is `Bre`. The default value is `Bre`. When Business Rules Engine is enabled for a Salesforce org, the default value is `Bre`. Other usage types may be available to you depending on your industry solution and permission sets. | Required | 59.0 |

          

        
        
          

**Response body for GET**

          
: [Lookup Tables Result
              List](./connect_responses_lookup_tables_result_list.htm.md)
