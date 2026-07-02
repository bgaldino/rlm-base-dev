---
page_id: connect_resources_get_procedure_plan_definition_by_ID.htm
title: Procedure Plan Definition By ID (GET, PATCH, DELETE)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_procedure_plan_definition_by_ID.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_business_apis_rest_references.htm
fetched_at: 2026-06-09
---

# Procedure Plan Definition By ID (GET, PATCH, DELETE)

Get, update, or delete a procedure plan definition record by using the
record ID.

Resource
:   ```
    /connect/procedure-plan-definitions/procedurePlanDefinitionId
    ```

    The
    `procedurePlanDefinitionId` property value is the
    ID or name of the procedure plan definition record to perform the request for.

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/procedure-plan-definitions/1FNxx0000004EsOGAU
    ```

Available version
:   62.0

HTTP methods
:   DELETE, GET, PATCH
:   You can delete a procedure plan definition only if it doesn’t include any active
    procedure plan version.

Response body for GET
:   [Procedure Plan
    Definition](./connect_responses_procedure_plan_definition_output.htm.md "Output representation of the details of a single procedure plan definition.")

Request body for PATCH
:   JSON example
    :   This example shows a sample request to update a
        procedure plan definition by using the Procedure Plan Definition By ID (PATCH) API.

        ![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

        #### Note

        The properties that aren’t specified in the input are deleted when updating the
        record.

        ```
        {
          "description": "Default definition patch update",
          "developerName": "Quote_Definition",
          "name": "Quote_Definition",
          "primaryObject": "Quote",
          "recordId": "1FNxx0000004EsOGAU"
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `description` | String | Description of the procedure plan definition. | Optional | 62.0 |
        | `developer​Name` | String | Developer name of the procedure plan definition. | Required if you’re invoking the [Procedure Plan Definitions API (POST)](./connect_resources_get_procedure_plan_definition_records.htm.md "Get the records of procedure plan definitions. Additionally, create a record of a procedure plan definition."). | 62.0 |
        | `name` | String | Name of the procedure plan definition. | Optional | 62.0 |
        | `primary​Object` | String | Source object that’s used to create a procedure with rule-based criteria. This property value must be a valid object name and must be unique in the ProcedurePlanDefinition object. | Required if you’re invoking the [Procedure Plan Definitions API (POST)](./connect_resources_get_procedure_plan_definition_records.htm.md "Get the records of procedure plan definitions. Additionally, create a record of a procedure plan definition.") and if you’re creating a procedure with rule-based criteria. | 62.0 |
        | `procedurePlan​Definition​Versions` | [Procedure Plan Definition Version Input](./connect_requests_procedure_plan_definition_version_input.htm.md "Input representation of the details of a procedure plan definition version.")[] | List of versions of a procedure plan definition. | Required | 62.0 |
        | `processType` | String | Specifies the business processes that need a procedure plan for each sObject and definition. Valid values are:   - `Billing` - `DRO` - `DeepClone` - `ProductDiscovery` - `Revenue Cloud`   These values can be used based on the available license. If unspecified, the value is set to `Default`. | Required | 63.0 |
        | `recordId` | String | ID of the procedure plan definition record. | Required if you’re invoking the [Procedure Plan Definition By ID API (PATCH)](# "Get, update, or delete a procedure plan definition record by using the record ID."). | 62.0 |

Response body for PATCH
:   [Procedure Plan
    Definition](./connect_responses_procedure_plan_definition_output.htm.md "Output representation of the details of a single procedure plan definition.")
