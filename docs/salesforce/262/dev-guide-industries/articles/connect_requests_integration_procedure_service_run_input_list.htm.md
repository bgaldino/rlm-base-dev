---
page_id: connect_requests_integration_procedure_service_run_input_list.htm
title: Integration Procedure Service Run Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_integration_procedure_service_run_input_list.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_integration_procedure_apis_requests.htm
fetched_at: 2026-06-25
---

# Integration Procedure Service Run Input

Input representation of the list of custom data to execute an integration procedure
from Apex.

JSON example
:   ```
    {
      "inputs": [
        "{\"Name\": \"Get Account Details\"}"
      ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `inputs` | String[] | List of configuration details for executing the integration procedures. | Required | 64.0 |
