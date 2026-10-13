---
page_id: connect_responses_playbook_contents_output.htm
title: Playbook Contents
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_playbook_contents_output.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Playbook Contents

Output representation that contains the playbook version ID and the
      matching content chunks.

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `chunks` | [Playbook Chunk](./connect_responses_playbook_chunk.htm.md)[] | List of matching content chunks. | Big, 68.0 | 68.0 |
| `playbookVersion​Id` | String | ID of the playbook version. | Big, 68.0 | 68.0 |

    

    

## JSON Example

      
      

```
{
  "chunks" : [ {
    "chunkText" : "Either party may terminate this agreement by providing 30 days' written notice.",
    "contentDocumentId" : "069xx0000004C92GAE",
    "contentDocumentTitle" : "Master Services Agreement Template",
    "score" : 0.8734
  }, {
    "chunkText" : "Payment is due within 45 days of the invoice date.",
    "contentDocumentId" : "069xx0000004C92GAE",
    "contentDocumentTitle" : "Master Services Agreement Template",
    "score" : 0.8021
  } ],
  "playbookVersionId" : "00OEE000003530L2AQ"
}
```
