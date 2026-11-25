---
page_id: connect-resources-create-query-tag
title: Query Tags (POST)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-create-query-tag.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: runtime-context-intance-management
legacy_page_id: connect_resources_create_query_tag.htm
fetched_at: 2026-11-25
---

# Query Tags (POST)

Create query tags within a defined context

## Resource

```
/connect/contexts/query-tags
```

## Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/contexts/query-tags
```

{yourInstance} is the domain name of your Salesforce instance.

## Available Version

59.0

## Requires Chatter

No

## HTTP Methods

POST

## Request Body for POST

### JSON Example

```
{
  "contextId": "3729ed60-d16d-41b8-8951-9ad4f6407ad2",
  "tags": [
    "Order"
  ]
}
```

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextId` | String | ID of the context record. | Required | 59.0 |
| `tags` | String[] | List of query tags to be queried within this context. | Required | 59.0 |

## Response Body for POST

[Query Tags Result](./connect-responses-query-tags-result.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-create-query-tag.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
