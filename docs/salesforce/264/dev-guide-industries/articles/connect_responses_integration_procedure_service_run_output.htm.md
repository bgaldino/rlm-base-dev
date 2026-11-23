---
page_id: connect_responses_integration_procedure_service_run_output.htm
title: Integration Procedure Execution Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_integration_procedure_service_run_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_integration_procedure_apis_responses.htm
fetched_at: 2026-11-23
---

# Integration Procedure Execution Details

Output representation of the execution details of the integration procedure.

## JSON Example

```
{
  "error": "Specify a valid IP name.",
  "response": [
    {
      "status": false
    }
  ],
  "status": "Error"
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | String | Error message if the execution of the integration procedure fails. | Small, 64.0 | 64.0 |
| `response` | String[] | List of responses for the execution of the integration procedures. | Small, 64.0 | 64.0 |
| `status` | String | Execution status of the integration procedure. Valid values are:  - `Error`—Execution has failed due to   an error. - `Success`—Execution is   successful. | Small, 64.0 | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_integration_procedure_service_run_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
