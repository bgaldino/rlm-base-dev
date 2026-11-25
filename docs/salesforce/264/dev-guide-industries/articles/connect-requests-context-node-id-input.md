---
page_id: connect-requests-context-node-id-input
title: Context Node ID Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-context-node-id-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-requests
legacy_page_id: connect_requests_context_node_id_input.htm
fetched_at: 2026-11-25
---

# Context Node ID Input

Input representation of the list of context node IDs to create the relationship nodes for.

## JSON Example

```
{
  "contextNodeIds": [
    "11oxx000001G3dtAAC",
    "11oxx000001G3duAAC"
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextNodeIds` | String | List of context node IDs to create the relationship nodes by adding them as child nodes to the context node that’s specified in the endpoint. | Required | 61.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-context-node-id-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
