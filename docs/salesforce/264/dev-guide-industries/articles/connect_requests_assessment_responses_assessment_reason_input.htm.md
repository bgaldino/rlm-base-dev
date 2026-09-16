---
page_id: connect_requests_assessment_responses_assessment_reason_input.htm
title: Assessment Reasons Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_assessment_responses_assessment_reason_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Discovery Framework
parent_page: dfdt_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Assessment Reasons Input

Input representation of the assessment reason in Assessment Response request. 

        
            
                
                    

**JSON example**

                    
: 
                        

```
{
        "assessmentReasons": [
            {
                "referenceRecord": "0jySG0000000qRdxxI"
            },
            {
                "referenceRecord": "0SqSG00000005HRxxY"
            },
            {
                "referenceRecord": "0kmSG0000000n7BxxQ",
                "referenceValue": "Medication Request sample"
            },
            {
                "referenceValue": "Reference Record not present"
            }
        ]
        }
    }
}
```

                    

                
                
                    

**Properties**

                    
: 
                        

                                
                                
                                
                                
                                
                                
                                    
                                        

                                        

                                        

                                        

                                        

                                    

                                

                                
                                    
                                        

                                        

                                        

                                        

                                        

                                    

                                    
                                        

                                        

                                        

                                        

                                        

                                    

                                

                            
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `referenceRecord` | String | Reason for the assessment. | Optional | 63.0 |
| `referenceValue` | String | The supporting information when there is no Salesforce record to be added as the reference record. | Optional | 63.0 |
