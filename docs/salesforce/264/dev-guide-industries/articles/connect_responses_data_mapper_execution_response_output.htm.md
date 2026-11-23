---
page_id: connect_responses_data_mapper_execution_response_output.htm
title: Data Mapper Execution Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_data_mapper_execution_response_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_data_mapper_apis_responses.htm
fetched_at: 2026-11-23
---

# Data Mapper Execution Response

Output representation of the response with error message, status, and response
type.

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
  ]
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | String | Error message if the execution fails for the input. | Small, 64.0 | 64.0 |
| `response` | String | Execution response corresponding to the custom input in JSON format. | Small, 64.0 | 64.0 |
| `responseType` | String | Format of the execution response, such as JSON, XML, or a custom class. | Small, 64.0 | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_data_mapper_execution_response_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
