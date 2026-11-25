---
page_id: connect-resources-context-query-lean-tag
title: Context Query Tags Leaner (POST)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-query-lean-tag.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-resources
legacy_page_id: connect_resources_context_query_lean_tag.htm
fetched_at: 2026-11-25
---

# Context Query Tags Leaner (POST)

Query tags and return a memory-optimized (leaner) result suitable for Apex and low-heap clients. Eliminate redundant metadata to reduce heap usage and payload size.

## Resource

```
/connect/contexts/query-tags-leaner
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/contexts/query-tags-leaner
```

{yourInstance} is the domain name of your Salesforce instance.

## Available Version

68.0

## HTTP Methods

POST

## Request Body for POST

### JSON Example

```
{
  "contextId": "0000000s07fm061002917633740427233ff03037a8fe48048696667781ec824c",
  "tags": [
    "Contact_FirstName",
    "Contact_Email"
  ]
}
```

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextId` | String | ID of the context to query. | Required | 66.0 |
| `tags` | String[] | List of tag names to query from the context. Tags can include both attribute-level and node-level. | Required | 66.0 |

## Response Body for POST

[Leaner Query Tags Result](./connect-responses-leaner-query-tags-result.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-query-lean-tag.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
