---
page_id: connect_responses_recipient_output.htm
title: Recipients Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_recipient_output.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Recipients Response

Output representation of a recipient’s personal and status information in a contract
    document’s signing process.

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `declined​Reason` | String | Declined reason for the signature. | Small, 61.0 | 61.0 |
| `email` | String | Email address of the recipient. | Small, 61.0 | 61.0 |
| `final​StatusDate​Time` | String | Final date and time of the current status. | Small, 61.0 | 61.0 |
| `name` | String | Name of the recipient. | Small, 61.0 | 61.0 |
| `status` | String | Status of the recipient. | Small, 61.0 | 61.0 |
| `type` | String | Type of the recipient. | Small, 61.0 | 61.0 |

    

    

## Sample Response

      
      

```
{
  "Name": "Rishyv Misrep",
  "email": "rishyv@salesforce.com",
  "status": "Signed",
  "finalStatusDateTime": ""
}
```
