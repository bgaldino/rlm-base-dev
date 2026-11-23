---
page_id: connect_responses_extraction_context_mappings_output.htm
title: Extraction Context Mappings
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_extraction_context_mappings_output.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-11-23
---

# Extraction Context Mappings

Output Representation to create and update extraction context mapping.

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the created mapping. | Small, 61.0 | 61.0 |
| `isSuccess` | Boolean | Indicates whether the mapping creation was successful (`true`) or not (`false`). | Small, 61.0 | 61.0 |
| `message` | String | Details of any error or warning messages. | Small, 61.0 | 61.0 |

## Sample Response

```
{
  "id": "map123",
  "isSuccess": true,
  "message": ""
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_extraction_context_mappings_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
