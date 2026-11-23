---
page_id: connect_responses_playbook_contents_output.htm
title: Playbook Contents
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_playbook_contents_output.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-11-23
---

# Playbook Contents

Output representation that contains the playbook version ID and the
matching content chunks.

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `chunks` | [Playbook Chunk](./connect_responses_playbook_chunk.htm.md "Output representation of a single playbook content chunk and its similarity score.")[] | List of matching content chunks. | Big, 68.0 | 68.0 |
| `playbookVersion​Id` | String | ID of the playbook version. | Big, 68.0 | 68.0 |

## JSON Example

```
{
  "chunks" : [ {
    "chunkText" : "Either party may terminate this agreement by providing 30 days' written notice.",
    "contentDocumentId" : "069xx0000004C92GAE",
    "contentDocumentTitle" : "Master Services Agreement Template",
    "score" : 0.8734
  }, {
    "chunkText" : "Payment is due within 45 days of the invoice date.",
    "contentDocumentId" : "069xx0000004C92GAE",
    "contentDocumentTitle" : "Master Services Agreement Template",
    "score" : 0.8021
  } ],
  "playbookVersionId" : "00OEE000003530L2AQ"
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_playbook_contents_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
