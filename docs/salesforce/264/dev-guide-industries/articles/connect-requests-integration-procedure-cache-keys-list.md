---
page_id: connect-requests-integration-procedure-cache-keys-list
title: Integration Procedure Cache Keys
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-integration-procedure-cache-keys-list.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-integration-procedure-apis-requests
legacy_page_id: connect_requests_integration_procedure_cache_keys_list.htm
fetched_at: 2026-11-25
---

# Integration Procedure Cache Keys

Input representation of the cache keys to clear the execution cache.

## JSON Example

```
{
    "cacheKeys": [
      "IP06535636"
    ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `cacheKeys` | String[] | List of cache keys to clear the cache for. | Optional | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-integration-procedure-cache-keys-list.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
