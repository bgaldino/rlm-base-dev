---
page_id: connect_responses_integration_procedure_service_run_output.htm
title: Integration Procedure Execution Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_integration_procedure_service_run_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_integration_procedure_apis_responses.htm
fetched_at: 2026-06-25
---

# Integration Procedure Execution Details

Output representation of the execution details of the integration procedure.

JSON example
:   ```
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
