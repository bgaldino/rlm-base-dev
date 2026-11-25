---
page_id: connect-requests-datamapper-cache-input-param
title: Data Mapper Clear Cache Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-datamapper-cache-input-param.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-data-mapper-apis-requests
legacy_page_id: connect_requests_datamapper_cache_input_param.htm
fetched_at: 2026-11-25
---

# Data Mapper Clear Cache Input

Input representation of the details to clear the cache of the data mappers.

## JSON Example

This is a sample example to clear the execution cache by using only the name of the data mapper.

```
{
  "cacheStorageType": "Metadata",
  "dataMapperList": {
    "dataMappers": [
      {
        "dataMapperName": "DRWithLoad"
      }
    ]
  }
}
```

This is a sample example to clear the execution cache by using the name of the data mapper along with additional inputs.

```
{
  "cacheStorageType": "Session",
  "dataMapperList": {
    "dataMappers": [
      {
        "dataMapperName": "DRWithLoad",
        "input": {
          "Name": "Get Account Details"
        }
      }
    ]
  }
}
```

## Properties

- 
- 
- 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `cacheStorageType` | String | Storage type that’s used for caching the data. Valid values are:`Session`—Cache is stored in the current user session.`Org`—Cache is shared across the entire organization.`All`—Refers to both session and org-level cache. | Required | 64.0 |
| `dataMapperList` | [Data Mapper Details](./connect-requests-data-mapper-details.md)[] | List of data mappers to clear the cache for. | Required | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-datamapper-cache-input-param.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
