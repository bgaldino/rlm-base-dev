---
page_id: connect_responses_content_link_list.htm
title: Content Link List
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_content_link_list.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Content Link List

Output representation of the content data for the specified reference IDs.

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contentLink​DataList` | [Content Link Detail[]](./connect_responses_content_link_detail.htm.md) | List of content links. | Small, 62.0 | 62.0 |
| `failedContent​LinkList` | [Failed Content Link List[]](./connect_responses_failed_content_link_list.htm.md) | List of failed content links. | Small, 62.0 | 62.0 |
| `reference​ObjectId` | String | ID of the reference object. | Small, 62.0 | 62.0 |

    

    

## JSON Sample

      
      

```
{
  "contentLinkDataList": [
    {
      "contentLinkId": "0D56A000008yhfSAAQ",
      "content": "Content data here"
    }
  ],
  "failedContentLinkList": [
    {
      "failedContentLinkId": "0D56A000008yhgTABQ",
      "failureReason": "Access denied"
    }
  ],
  "referenceObjectId": "a0X4W00000X8jklUAB"
}
```
