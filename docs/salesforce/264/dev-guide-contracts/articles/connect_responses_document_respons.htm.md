---
page_id: connect_responses_document_respons.htm
title: Document Record
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_document_respons.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Document Record

Document record.

    

## Properties

      
      

            
            
            
            
            
            
                
                    

                    

                    

                    

                    

                

            

            
                
                    

                    

                    

                    

                    

                

                
                    

                    

                    

                    

                    

                

                
                    

                    

                    

                    

                    

                

                
                    

                    

                    

                    

                    

                

                
                    

                    

                    

                    

                    

                

            

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `additionalFields` | Map<String, String> | Additional fields related to document for custom implementation. | Big, 56.0 | 56.0 |
| `fileExtension` | String | The file extension of document. | Small, 56.0 | 56.0 |
| `name` | String | The name of document. | Small, 56.0 | 56.0 |
| `sourceId` | String | The source ID of document. | Small, 56.0 | 56.0 |
| `sourceType` | String | The source type of document. | Small, 56.0 | 56.0 |

    

    

## Response Example

      
      

```

{
    "documents": 
    [
       
        {
            "name":"docx-template",
            "sourceId": "800xx000000boTRAAY",
            "fileExtension":"docx",            
            "sourceType":"Content",
            "additionalFields":
                {
                    "key1": "value1"
                }
        },
        {
            "name":"annual-contract-doc",
            "sourceId": "800xx000000boQTFGS",
            "fileExtension":"pdf",            
            "sourceType":"Content",
            "additionalFields":
                {
                    "key1": "value1",
                    "key2": "value2"
                }
        }
    ]
}
```
