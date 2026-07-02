---
page_id: connect_responses_data_mapper_execution_output.htm
title: Data Mapper Execution Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_data_mapper_execution_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_data_mapper_apis_responses.htm
fetched_at: 2026-06-25
---

# Data Mapper Execution Details

Output representation of the execution details of a data mapper.

JSON example
:   ```
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

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | String | Error message if the execution fails. | Small, 64.0 | 64.0 |
| `response` | [Data Mapper Execution Response](./connect_responses_data_mapper_execution_response_output.htm.md "Output representation of the response with error message, status, and response type.") [] | List of responses corresponding to the custom inputs that are provided during the data mapper execution. | Small, 64.0 | 64.0 |
| `status` | String | Execution status of the data mapper. Valid values are:  - `Error`—Data mapper execution has   failed due to an error. - `Success`—Data mapper execution is   successful. | Small, 64.0 | 64.0 |
