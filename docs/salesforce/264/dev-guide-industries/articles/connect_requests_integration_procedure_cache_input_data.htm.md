---
page_id: connect_requests_integration_procedure_cache_input_data.htm
title: Integration Procedure Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_integration_procedure_cache_input_data.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_integration_procedure_apis_requests.htm
fetched_at: 2026-11-23
---

# Integration Procedure Details

Input representation of the details of the integration procedures to clear the cache
for.

## JSON Example

```
{
  "inputs": [
    {
      "ipkey": "Account_GetAccountDetails",
      "inputData": "{\"Name\": \"Get Account Details\"}",
      "blockName": "Cache"
    }
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `blockName` | String | Block name of the integration procedure. | Optional | 64.0 |
| `iPKey` | String | Unique key that's associated with the integration procedure. The format of the value for this property is `Type_SubType`. | Required | 64.0 |
| `inputData` | String | Additional data to clear the cache. | Optional | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_integration_procedure_cache_input_data.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
