---
page_id: connect_requests_integration_procedure_cache_input.htm
title: Integration Procedure Clear Cache Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_integration_procedure_cache_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_integration_procedure_apis_requests.htm
fetched_at: 2026-11-23
---

# Integration Procedure Clear Cache Input

Input representation of the details to clear the execution cache of the integration
procedures.

## JSON Example

This is a sample example to clear the cache of an integration procedure by using the
key that's associated with the integration procedure and cache storage type.

```
{
  "cacheStorageType": "Metadata",
  "ipInput": {
    "inputs": [
      {
        "ipkey": "Account_GetAccountDetails"
      }
    ]
  }
}
```

This is a sample example to clear the cache of an integration procedure by using the
cache keys and cache storage type.

```
{
  "cacheKeys": {
    "cacheKeys": [
      "IP06535636"
    ]
  },
  "cacheStorageType": "Metadata"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `cacheKeys` | [Integration Procedure Cache Keys](./connect_requests_integration_procedure_cache_keys_list.htm.md "Input representation of the cache keys to clear the execution cache.") | List of cache keys to clear the cache for. Cache keys are used to identify the cached data. | Optional | 64.0 |
| `cacheStorageType` | String | Storage type that's used for caching the data. Valid values are:  - `All`—Includes all cache   types, such as metadata, session, and org-level caches. - `Metadata`—Cache is used for   configuration-related data such as schemas or field mappings. - `Org`—Cache is shared across   the entire organization. - `Session`—Cache is stored in   the current user session. | Required | 64.0 |
| `iPInput` | [Integration Procedure Details](./connect_requests_integration_procedure_cache_input_data.htm.md "Input representation of the details of the integration procedures to clear the cache for.")[] | List of integration procedures to clear the cache for. | Optional | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_integration_procedure_cache_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
