---
page_id: connect_responses_envelope_status_list_respons.htm
title: Envelope Status List
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_envelope_status_list_respons.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Envelope Status List

Output representation of the envelope status update
    request.

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `signatureStatus` | [Envelope Status[]](./connect_responses_envelope_status_respons.htm.md) | List of all the envelope IDs with their status. | Small, 56.0 | 56.0 |
| `sourceObjectId` | String | ID of the parent object. | Small, 56.0 | 56.0 |
| `totalEnvelopes​ToBeUpdated` | Integer | Total number of envelopes to be updated. | Small, 56.0 | 56.0 |
| `totalEnvelopes​Updated` | Integer | Actual count of envelopes updated. | Small, 56.0 | 56.0 |

    

    

## JSON Example

      
      

```

{
   "totalEnvelopesToBeUpdated":"",
   "totalEnvelopesUpdated":"",
   "signatureStatus:{"envelopeId1":{"success":false,"error":"errorcode","message":"errormessage"},
                          "envelopeId2":{"success":true, status:"Completed"}}
}
```
