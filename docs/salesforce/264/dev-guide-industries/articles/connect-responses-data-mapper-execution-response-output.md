---
page_id: connect-responses-data-mapper-execution-response-output
title: Data Mapper Execution Response
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-data-mapper-execution-response-output.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-data-mapper-apis-responses
legacy_page_id: connect_responses_data_mapper_execution_response_output.htm
fetched_at: 2026-11-25
---

# Data Mapper Execution Response

Output representation of the response with error message, status, and response type.

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

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-data-mapper-execution-response-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
