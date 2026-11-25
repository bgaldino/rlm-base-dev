---
page_id: connect-responses-data-mapper-execution-output
title: Data Mapper Execution Details
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-data-mapper-execution-output.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-data-mapper-apis-responses
legacy_page_id: connect_responses_data_mapper_execution_output.htm
fetched_at: 2026-11-25
---

# Data Mapper Execution Details

Output representation of the execution details of a data mapper.

## JSON Example

```
{
  "response": [
    {
      "error": "Specify a Data Mapper name",
      "response": [
        {
          "status": false
        }
      ],
      "responseType": "JSON"
    }
  ],
  "status": "Success"
}
```

## Properties

- 
- 

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | String | Error message if the execution fails. | Small, 64.0 | 64.0 |
| `response` | [Data Mapper Execution Response](./connect-responses-data-mapper-execution-response-output.md) [] | List of responses corresponding to the custom inputs that are provided during the data mapper execution. | Small, 64.0 | 64.0 |
| `status` | String | Execution status of the data mapper. Valid values are:`Error`—Data mapper execution has failed due to an error.`Success`—Data mapper execution is successful. | Small, 64.0 | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-data-mapper-execution-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
