---
page_id: connect_requests_integration_procedure_service_run_input.htm
title: Integration Procedure Service Run
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_integration_procedure_service_run_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_integration_procedure_apis_requests.htm
fetched_at: 2026-06-25
---

# Integration Procedure Service Run

Input representation of the details to execute an integration procedure from
Apex.

JSON example
:   ```
    {
      "input": {
        "inputs": [
          "{\"Name\": \"Get Account Details\"}"
        ]
      },
      "options": {
        "ignoreCache": false
      }
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `input` | [Integration Procedure Service Run Input](./connect_requests_integration_procedure_service_run_input_list.htm.md "Input representation of the list of custom data to execute an integration procedure from Apex.") | Details to execute the integration procedure. | Required | 64.0 |
    | `options` | [Integration Procedure Service Run Options](./connect_requests_integration_procedure_service_run_options.htm.md "Input representation of the optional parameters to customize and refine the execution of the integration procedure.") | Optional parameters to refine the execution of the integration procedure. | Optional | 64.0 |
