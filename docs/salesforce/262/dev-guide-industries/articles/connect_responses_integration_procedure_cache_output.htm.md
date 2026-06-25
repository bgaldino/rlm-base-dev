---
page_id: connect_responses_integration_procedure_cache_output.htm
title: Integration Procedure Cache Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_integration_procedure_cache_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_integration_procedure_apis_responses.htm
fetched_at: 2026-06-25
---

# Integration Procedure Cache Details

Output representation of the cache that are cleared for the specified integration
procedures.

JSON example
:   ```
    {
      "error": "Specify a valid cache key.",
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
| `error` | String | Error message if the operation fails. | Small, 64.0 | 64.0 |
| `responseList` | [Integration Procedure Cache Response](./connect_responses_integration_procedure_cache_response.htm.md "Output representation of the response with error message and status.")[] | List of responses that are generated during the cache clearing process where each response corresponds to a specific cache key. | Small, 64.0 | 64.0 |
| `status` | Boolean | Indicates whether the cache is cleared successfully (`true`) or not (`false`) | Small, 64.0 | 64.0 |
