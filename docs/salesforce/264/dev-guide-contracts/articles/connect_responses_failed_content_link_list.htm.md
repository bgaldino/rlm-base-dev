---
page_id: connect_responses_failed_content_link_list.htm
title: Failed Content Link List
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_failed_content_link_list.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-11-23
---

# Failed Content Link List

Output representation of the content ID and error details for the failed
requests.

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `failedContent​LinkId` | String | ID of the content link associated with the failure. | Small, 62.0 | 62.0 |
| `failureReason` | String | Reason for the API request's failure to fetch the content link. | Small, 62.0 | 62.0 |

## JSON Sample

```
{
  "failedContentLinkList": [
    {
      "failedContentLinkId": "0D56A000008yhgTABQ",
      "failureReason": "Access denied"
    }
  ]
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_failed_content_link_list.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
