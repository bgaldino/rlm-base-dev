---
page_id: connect_responses_playbook_chunk.htm
title: Playbook Chunk
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_playbook_chunk.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Playbook Chunk

Output representation of a single playbook content chunk and its
      similarity score.

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `chunkText` | String | Text content of the chunk. | Big, 68.0 | 68.0 |
| `contentDocument​Id` | String | ID of the content document that contains this chunk. | Big, 68.0 | 68.0 |
| `contentDocument​Title` | String | Title of the content document. | Big, 68.0 | 68.0 |
| `score` | Double | Similarity score of the chunk to the query. | Big, 68.0 | 68.0 |

    

    

## JSON Example

      
      

```
{
  "chunkText" : "Either party may terminate this agreement by providing 30 days' written notice.",
  "contentDocumentId" : "069xx0000004C92GAE",
  "contentDocumentTitle" : "Master Services Agreement Template",
  "score" : 0.8734
}
```
