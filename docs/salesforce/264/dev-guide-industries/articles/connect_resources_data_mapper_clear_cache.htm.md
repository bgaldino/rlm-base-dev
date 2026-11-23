---
page_id: connect_resources_data_mapper_clear_cache.htm
title: Data Mapper Clear Cache (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_data_mapper_clear_cache.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_data_mapper_apis_resources.htm
fetched_at: 2026-11-23
---

# Data Mapper Clear Cache (POST)

Clear the execution cache for the specified data mappers.

## Resource

```
/connect/omni-global/data-mapper/actions/clear-cache
```

## Available Version

64.0

## HTTP Methods

POST

## Request Body for POST

### JSON Example

This is a sample example to clear the execution cache by using only the name of the
data mapper.

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

This is a sample example to clear the execution cache by using the name of the data
mapper along with additional inputs.

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

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `cacheStorageType` | String | Storage type that's used for caching the data. Valid values are:  - `Session`—Cache is stored in   the current user session. - `Org`—Cache is shared across   the entire organization. - `All`—Refers to both session   and org-level cache. | Required | 64.0 |
| `dataMapperList` | [Data Mapper Details](./connect_requests_data_mapper_details.htm.md "Input representation of the data mapper details to clear the cache for.")[] | List of data mappers to clear the cache for. | Required | 64.0 |

## Response Body for POST

[Data Mapper Cache
Details](./connect_responses_datamapper_clear_cache_output.htm.md "Output representation of the cache details that are cleared for the specified data mappers.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_data_mapper_clear_cache.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
