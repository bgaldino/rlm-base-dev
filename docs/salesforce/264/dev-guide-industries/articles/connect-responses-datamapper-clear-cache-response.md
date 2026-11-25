---
page_id: connect-responses-datamapper-clear-cache-response
title: Data Mapper Cache Response
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-datamapper-clear-cache-response.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-data-mapper-apis-responses
legacy_page_id: connect_responses_datamapper_clear_cache_response.htm
fetched_at: 2026-11-25
---

# Data Mapper Cache Response

Output representation of the response with error message and status.

## JSON Example

```
{
  "responseList": [
    {
      "status": true
    }
  ]
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | String | Error message if the operation fails. | Small, 64.0 | 64.0 |
| `status` | Boolean | Indicates whether the cache is cleared successfully (`true`) or not (`false`). | Small, 64.0 | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-datamapper-clear-cache-response.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
