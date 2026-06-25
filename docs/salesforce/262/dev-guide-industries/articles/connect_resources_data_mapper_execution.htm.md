---
page_id: connect_resources_data_mapper_execution.htm
title: Data Mapper Execution (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_data_mapper_execution.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_data_mapper_apis_resources.htm
fetched_at: 2026-06-25
---

# Data Mapper Execution (POST)

Execute a data mapper from Apex classes by specifying the name of the data mapper along
with additional inputs and options.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

When using the Data Mapper (DM) Connect API, HTTP callouts cannot
be executed in the same transaction. This is because these APIs perform an implicit DML
operation through the underlying Connect API framework. If a callout is required, it must be
executed in a separate transaction, for example by using an asynchronous mechanism such as
@future.

Resource
:   ```
    /connect/omni-global/data-mapper/execute/name
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/omni-global/data-mapper/execute/Get Account Details
    ```

Available version
:   64.0

HTTP methods
:   POST

Path parameter for POST
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `name` | String | Name of the data mapper. | Required | 64.0 |

Request body for POST
:   JSON example
    :   ```
        {
          "dataMapperInput": {
            "inputs": [
              {
                "Name": "Get Account Details"
              }
            ]
          },
          "inputType": "JSON",
          "options": {
            "ignoreCache": false
          }
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `dataMapperInput` | [Data Mapper Execute Input Data](./connect_requests_data_mapper_execute_input_data.htm.md "Input representation of the list of custom data for the execution of the data mapper.") | Details for executing the data mapper. | Required | 64.0 |
        | `inputType` | String | Type of data mapper input. For example, JSON, XML, or custom class. | Required | 64.0 |
        | `options` | [Data Mapper Execution Options](./connect_requests_data_mapper_execution_options.htm.md "Input representation of the optional parameters for the data mapper execution.") | Optional parameters to refine the data mapper execution. | Optional | 64.0 |

Response body for POST
:   [Data Mapper Execution
    Details](./connect_responses_data_mapper_execution_output.htm.md "Output representation of the execution details of a data mapper.")
