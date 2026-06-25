---
page_id: connect_resources_integration_procedure.htm
title: Integration Procedure Execution (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_integration_procedure.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_integration_procedure_apis_resources.htm
fetched_at: 2026-06-25
---

# Integration Procedure Execution (POST)

Execute an integration procedure by using the name or ID of the integration
procedure.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

When using the Integration Procedure (IP) Connect API, HTTP
callouts cannot be executed in the same transaction. This is because these APIs perform an
implicit DML operation through the underlying Connect API framework. If a callout is
required, it must be executed in a separate transaction, for example by using an
asynchronous mechanism such as @future.

Resource
:   ```
    /connect/omni-global/integration-procedure/execute/id
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/omni-global/integration-procedure/execute/0jNxx000000005rFCC
    ```

Available version
:   64.0

HTTP methods
:   POST

Path parameter for POST
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `id` | String | Name or ID of the integration procedure. | Required | 64.0 |

Request body for POST
:   JSON example
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

Response body for POST
:   [Integration Procedure
    Execution Details](./connect_responses_integration_procedure_service_run_output.htm.md "Output representation of the execution details of the integration procedure.")
