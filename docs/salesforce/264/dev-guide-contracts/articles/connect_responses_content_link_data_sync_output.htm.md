---
page_id: connect_responses_content_link_data_sync_output.htm
title: Content Link Data Sync
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_content_link_data_sync_output.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Content Link Data Sync

Output representation that contains the details of data synchronization with success and
    failure information.

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `failedContent​LinkDataList` | [Content Link Data Sync Detail](./connect_responses_content_link_data_sync_detail.htm.md)[] | List of content links that failed to update, including error details. | Small, 65.0 | 65.0 |
| `reference​ObjectId` | String | ID of the sObjects that were updated. | Small, 65.0 | 65.0 |
| `saveCommitted` | Boolean | Indicates whether successful transactions were committed to the database (`true`) or not (`false`). | Small, 65.0 | 65.0 |
| `successContent​LinkDataList` | [Content Link Data Sync Detail](./connect_responses_content_link_data_sync_detail.htm.md)[] | List of content links that were successfully updated. | Small, 65.0 | 65.0 |

    

    

## JSON Example

      
      

```
{
  "failedContentLinkDataList": [
    {
      "contentLinkId": "6UPxx0000004CCGGA2",
      "failureReason": "Contract Term: value not of required type: 3",
      "isSuccess": false,
      "value": "3"
    }
  ],
  "referenceObjectId": "069xx0000004CsCAAU",
  "saveCommitted": false,
  "successContentLinkDataList": [
    {
      "contentLinkId": "6UPxx0000004C92GAE",
      "isSuccess": true,
      "value": "Contract Description for JSON"
    }
  ]
}
```
