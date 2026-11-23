---
page_id: connect_responses_content_link_data_sync_detail.htm
title: Content Link Data Sync Detail
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_content_link_data_sync_detail.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-11-23
---

# Content Link Data Sync Detail

Output representation that contains content link details for the requested
IDs.

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contentLinkId` | String | Record ID of the content link. | Small, 65.0 | 65.0 |
| `failureReason` | String | Reason for the failure, if the `isSuccess` property value is `false`. | Small, 65.0 | 65.0 |
| `isSuccess` | Boolean | Indicates whether the data sync validation was successful (`true`) or not (`false`). | Small, 65.0 | 65.0 |
| `value` | String | Represents the data for the content. | Small, 65.0 | 65.0 |

## JSON Example

```
{
  "contentLinkId": "6UPxx0000004CCGGA2",
  "value": "3",
  "isSuccess": false,
  "failureReason": "Contract Term: value not of required type: 3"
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_content_link_data_sync_detail.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
