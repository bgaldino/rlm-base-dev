---
page_id: connect_requests_data_mapper_execute_input_data.htm
title: Data Mapper Execute Input Data
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_data_mapper_execute_input_data.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_data_mapper_apis_requests.htm
fetched_at: 2026-11-23
---

# Data Mapper Execute Input Data

Input representation of the list of custom data for the execution of the data
mapper.

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

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_data_mapper_execute_input_data.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
