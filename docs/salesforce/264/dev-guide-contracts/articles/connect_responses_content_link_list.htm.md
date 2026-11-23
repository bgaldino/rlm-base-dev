---
page_id: connect_responses_content_link_list.htm
title: Content Link List
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_content_link_list.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-11-23
---

# Content Link List

Output representation of the content data for the specified reference IDs.

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contentLink​DataList` | [Content Link Detail[]](./connect_responses_content_link_detail.htm.md "Output representation of the content link details for the specified reference IDs.") | List of content links. | Small, 62.0 | 62.0 |
| `failedContent​LinkList` | [Failed Content Link List[]](./connect_responses_failed_content_link_list.htm.md "Output representation of the content ID and error details for the failed requests.") | List of failed content links. | Small, 62.0 | 62.0 |
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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_content_link_list.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
