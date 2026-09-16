---
page_id: connect_resources_bre_expression_set.htm
title: Expression Set Invocation (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_expression_set.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Expression Set Invocation (POST)

Invokes expression sets in Business Rule Engine.

    
      
        
          

**Resource**

          
: 
            

```
/connect/business-rules/expressionSet/${expressionSetName}
```

          

        
        
          

**Resource Example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/vXX.X/connect
/business-rules/expressionSet/${expressionSetName}
```

            
            
          

        
        
          

**Available version**

          
: 55.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
: POST

        
        
          

**Request body for POST**

          
: 
            
        
          

**JSON example 1**

          
: 
            

```
{
  "inputs": [
    {
      "age": "25",
      "state": "CA",
      "PatientId": "001xx000003GYjnAAG"
    }
  ],
  "options": {
    "effectiveDate": "2022-12-03T10:15:30Z",
    "useDatesOnly": "true",
    "actionContextCode": "9QLxx0000004C92GAE",
    "explainabilitySpecName": "ES_One_Explainability"
  }
}
```

          

        
        
          

**JSON example 2**

          
: 
            

```
{
  "inputs": [
    {
      "age": "25",
      "state": "CA",
      "PatientId":"001xx000003GYjnAAG",
      "__actionContextCode":"001xx000003GYjnAAG"
    }
  ],
  "options": {
    "effectiveDate": "2022-12-03T10:15:30Z",
    "useDatesOnly": "true"
  }
}

```

            

#### Note

You can use more than one `actionContextCode`
              for multiple sets of inputs, passed in a single API call. 

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

#### 

- 
- 

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `inputs` | Map<String, Object>[] | List of inputs passed to an expression set. An input may contain multiple variables. Note If the expression set uses a field alias as a variable, append Id to the object alias to which the field alias belongs, and pass the ID of the source object linked to the object alias. If the expression set uses a context definition, append Id to the context definition developer name and pass the context ID as the value. | Required | 55.0 |
| `options` | [Expression Set Options Input](./connect_requests_options.htm.md) | The options for executing an expression set. | Optional | 55.0 |

          

        
      

          

        
        
          

**Response body for POST**

          
: [Business Rules Result](./connect_responses_business_rules_result.htm.md)
