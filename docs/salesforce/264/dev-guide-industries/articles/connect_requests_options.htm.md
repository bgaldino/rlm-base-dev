---
page_id: connect_requests_options.htm
title: Expression Set Options Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_options.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Expression Set Options Input

Input representation of the options for executing an expression
      set.

    
      
        
          

**JSON example**

          
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

          

        
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

#### 

                    

                    

                  

                  
                    

                    

                    

#### 

                    

                    

                  

                  
                    

                    

                    

#### 

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `actionContext​Code` | String | The code of the action context used to log explainability for a specific execution of an expression set. Note To exclude decision explanations for expression set version steps from action logs, ensure that you exclude the `actionContextCode` and `explainabilitySpecName` properties from the payload. | Optional | 55.0 |
| `effectiveDate` | String | The date from which an expression set comes into effect. The date format is yyyy-mm-dd’T’hh:mm:ss’Z. Note Multiple versions of an expression set can exist with different date ranges. For example, Version 1 is effective before December 2019, and Version 2 is effective from January 2020 to the present. If you specify `effectiveDate` as "2019-03-15T00:00:00Z", Version 1 is executed. If you do not specify `effectiveDate`, the currently active version, Version 2, is executed. | Optional | 55.0 |
| `explainability​Spec​Name` | String | The name of the explainability specification that is used to log explainability for a specific execution of an expression set. Note To exclude decision explanations for expression set version steps from action logs, ensure that you exclude the `actionContextCode` and `explainabilitySpecName` properties from the payload. | Optional | 55.0 |
| `useDatesOnly` | String | Specifies that only the date portion (yyyy-mm-dd) of the value of effectiveDate field is to be used at the time of execution. | Optional | 55.0 |
| `versionNumber` | String | The version number of the expression set version record. | Optional | 55.0 |
