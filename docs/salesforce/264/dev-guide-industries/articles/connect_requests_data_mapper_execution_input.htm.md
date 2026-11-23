---
page_id: connect_requests_data_mapper_execution_input.htm
title: Data Mapper Execution Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_data_mapper_execution_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_data_mapper_apis_requests.htm
fetched_at: 2026-11-23
---

# Data Mapper Execution Input

Input representation of the execution details of a data mapper.

## JSON Example

```
{
  "dataMapperInput": {
    "inputs": [
      {
        "Name": "Get Account Details"
      }
    ]
  },
  "inputType": "JSON",
  "options": {
    "ignoreCache": false
  }
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `dataMapperInput` | [Data Mapper Execute Input Data](./connect_requests_data_mapper_execute_input_data.htm.md "Input representation of the list of custom data for the execution of the data mapper.") | Details for executing the data mapper. | Required | 64.0 |
| `inputType` | String | Type of data mapper input. For example, JSON, XML, or custom class. | Required | 64.0 |
| `options` | [Data Mapper Execution Options](./connect_requests_data_mapper_execution_options.htm.md "Input representation of the optional parameters for the data mapper execution.") | Optional parameters to refine the data mapper execution. | Optional | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_data_mapper_execution_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
