---
page_id: connect-requests-data-mapper-execute-input-data
title: Data Mapper Execute Input Data
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-data-mapper-execute-input-data.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-data-mapper-apis-requests
legacy_page_id: connect_requests_data_mapper_execute_input_data.htm
fetched_at: 2026-11-25
---

# Data Mapper Execute Input Data

Input representation of the list of custom data for the execution of the data mapper.

## JSON Example

```
{
  "inputs": [
    {
      "Name": "Get Account Details"
    }
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `inputs` | String[] | List of configuration details for executing the data mappers. | Required | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-data-mapper-execute-input-data.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
