---
page_id: connect_requests_content_link_input.htm
title: Content Link Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_content_link_input.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_requests.htm
fetched_at: 2026-11-23
---

# Content Link Input

Input representation of the request to fetch the content token data from the ContentLink
object.

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `content​LinkIds` | String[] | List of the content link IDs to fetch the data. | Optional | 62.0 |
| `isBulk​Request` | Boolean | Indicates whether fields associated with the same object ID are grouped and fetched together in a single bulk request (`true`) or not (`false`). | Optional | 66.0 |
| `reference​ObjectId` | String | ID of the reference object to retrieve the content data. | Optional | 62.0 |

## JSON Example

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_content_link_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
