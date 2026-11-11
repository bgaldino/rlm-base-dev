---
page_id: connect_resources_contentlink_data_sync.htm
title: Data Sync (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_contentlink_data_sync.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_data_true_up_resources.htm
fetched_at: 2026-10-13
---

# Data Sync (POST)

Synchronize and save the updated values for a specified reference ID
      and a set of content link IDs.

    

## Resource

      
      

```
/connect/content-link/data-sync
```

    

    

## Resource Example

      
      

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/content-link/data-sync
```

    

    

## Available Version

      
      

65.0

    

    

## HTTP Methods

      
      

POST

    

    

## Request Body for POST

      
      

**JSON Example**

      

```
{
  "referenceObjectId": "069xx0000004CsCAAU",
  "partialCommit": "false",
  "isBulkRequest": "false",
  "contentLinkDetailsList": [
    {
      "contentLinkId": "6UPVW00000003CQ4AY",
      "contentValue": "Contract Description for JSON"
    },
    {
      "contentLinkId": "6UPxx0000004CCGGA2",
      "contentValue": "3"
    }
  ]
}
```

      

**Properties**

      

                        
                          

                          

                          

                          

                          

                        

                        
                          

                          

                          

                          

                          

                        

                        
                          

                          

                          

                          

                          

                        

                        
                          

                          

                          

                          

                          

                        

                      

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contentLink​DetailsList` | [Content Link Details Input](./connect_requests_content_link_details_input.htm.md)[] | List of content link records with their IDs and updated values. Each object includes a contentLinkId and a contentValue property value. | Required | 65.0 |
| `isBulk​Request` | Boolean | Indicates whether fields associated with the same object ID are grouped and fetched together in a single bulk request (`true`) or not (`false`). | Optional | 66.0 |
| `partialCommit` | Boolean | Indicates whether successful records should be committed in case of partial errors (`true`) or not (`false`). The default value is `false`. | Optional | 65.0 |
| `reference​ObjectId` | String | ID of the target Salesforce object that must be updated, such as a Contract record. | Optional | 65.0 |

    

    

## Response Body for POST

      
      

[Content Link Data Sync](./connect_responses_content_link_data_sync_output.htm.md)
