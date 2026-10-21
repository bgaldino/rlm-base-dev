---
page_id: connect_resources_contentlink_load.htm
title: Content Link Load (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_contentlink_load.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_data_true_up_resources.htm
fetched_at: 2026-10-13
---

# Content Link Load (POST)

Fetches the content data for a specified reference ID or set of
      content link IDs.

    

## Resource

      
      

```
/connect/content-link/load
```

    

    

## Example POST

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v68.0/connect/content-link/load
```

    

    

## Available Version

      
      

62.0

    

    

## HTTP Methods

      
      

POST

    

    

## Request Body for POST

      
      

**JSON Example**

      

```
{
  "referenceObjectId": "a0X4W00000X8jklUAB",
  "isBulkRequest": "false",
  "contentLinkIds": [
    "0D56A000008yhfSAAQ",
    "0D56A000008yhgTABQ"
  ]
}
```

      

**Properties**

      

                        
                          

                          

                          

                          

                          

                        

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `content​LinkIds` | String[] | List of the content link IDs to fetch the data. | Optional | 62.0 |
| `isBulk​Request` | Boolean | Indicates whether fields associated with the same object ID are grouped and fetched together in a single bulk request (`true`) or not (`false`). | Optional | 66.0 |
| `reference​ObjectId` | String | ID of the reference object to retrieve the content data. | Optional | 62.0 |

    

    

## Response Body for POST

      
      

[Content Link List](./connect_responses_content_link_list.htm.md)
