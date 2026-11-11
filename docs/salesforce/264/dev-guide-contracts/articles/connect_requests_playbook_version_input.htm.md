---
page_id: connect_requests_playbook_version_input.htm
title: Playbook Version Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_playbook_version_input.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_requests.htm
fetched_at: 2026-10-13
---

# Playbook Version Input

Input representation for creating a playbook version.

    

## Properties

      
      

            
            
            
            
            
            
              
                

                

                

                

                

              

            

            
              
                

                

                

                

                

              

              
                

                

                

                

                

              

              
                

                

                

                

                

              

            

          
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contentDocument​Id` | String | ID of the content document. | Required | 68.0 |
| `description` | String | Description of the playbook version. | Optional | 68.0 |
| `playbookId` | String | ID of the playbook. | Required | 68.0 |

    

    

## JSON Example

      
      

```

{
  "playbookId" : "0RDxx0000004C92GAE",
  "description" : "Initial version of the contract playbook",
  "contentDocumentId" : "069xx0000004C92GAE"
}
```
