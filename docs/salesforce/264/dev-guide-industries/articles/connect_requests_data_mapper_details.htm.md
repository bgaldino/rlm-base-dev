---
page_id: connect_requests_data_mapper_details.htm
title: Data Mapper Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_data_mapper_details.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_data_mapper_apis_requests.htm
fetched_at: 2026-11-23
---

# Data Mapper Details

Input representation of the data mapper details to clear the cache for.

## JSON Example

```
{
  "dataMappers": [
    {
      "dataMapperName": "DRWithLoad",
      "input": {
        "Name": "Get Account Details"
      }
    }
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `dataMapperName` | String | Name of the data mapper to clear the cache for. The execution cache is cleared for the storage that's specified in the `cacheStorageType` property. | Required | 64.0 |
| `input` | String | Custom JSON data to clear the cache. | Optional | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_data_mapper_details.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
