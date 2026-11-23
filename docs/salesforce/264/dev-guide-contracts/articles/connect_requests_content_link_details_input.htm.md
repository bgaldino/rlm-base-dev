---
page_id: connect_requests_content_link_details_input.htm
title: Content Link Details Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_content_link_details_input.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_requests.htm
fetched_at: 2026-11-23
---

# Content Link Details Input

Input representation of the request to synchronize content token data from a document to
sObjects. It specifies the ID of an individual content link and its corresponding new value to
be updated.

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contentLinkId` | String | ID of the content link object. | Required | 65.0 |
| `contentValue` | String | Updated token value data from the document. | Required | 65.0 |

## JSON Example

```
{
  "contentLinkId": "6UPxx0000004C92GAE",
  "contentValue": "Contract Description for JSON"
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_content_link_details_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
