---
page_id: connect-requests-data-mapper-execution-input
title: Data Mapper Execution Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-data-mapper-execution-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-data-mapper-apis-requests
legacy_page_id: connect_requests_data_mapper_execution_input.htm
fetched_at: 2026-11-25
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
| `dataMapperInput` | [Data Mapper Execute Input Data](./connect-requests-data-mapper-execute-input-data.md) | Details for executing the data mapper. | Required | 64.0 |
| `inputType` | String | Type of data mapper input. For example, JSON, XML, or custom class. | Required | 64.0 |
| `options` | [Data Mapper Execution Options](./connect-requests-data-mapper-execution-options.md) | Optional parameters to refine the data mapper execution. | Optional | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-data-mapper-execution-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
