---
page_id: connect_responses_procedure_plan_definition_output.htm
title: Procedure Plan Definition
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_procedure_plan_definition_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Procedure Plan Definition

Output representation of the details of a single procedure plan definition.

JSON example
:   This example shows a sample response for the Procedure Plan Definition By ID (GET)
    request.

    ```
           {
         "description": "Default Definition",
         "developerName": "Quote_Definition",
         "name": "Quote_Definition",
         "primaryObject": "Quote",
         "procedurePlanDefinitionVersions": [
         {
          "active": false,
          "contextDefinition": "11Oxx0000006PZ7EAM",
          "effectiveFrom": "2024-02-03T10:15:30.000Z",
          "effectiveTo": "2024-02-03T10:15:30.000Z",
          "readContextMapping": "MedicalHistoryMapping",
          "recordId": "1Cvxx0000004E1ACAU",
          "saveContextMapping": "MedicalHistoryMapping",
          "success": true,
          "processType": "Default"
        }
      ],
      "recordId": "1FNxx0000004GkWGAU",
      "processType": "Default",
      "success": true
    }
    ```
:   This example shows a sample response for the Procedure Plan Definition By ID (PATCH)
    request.

    ```
      {
      "procedurePlanDefinitionVersions":[],
      "recordId":"1FNDU00000000EX4AY",
      "processType": "Default",
      "success":true
      }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `description` | String | Description for the procedure plan definition. | Small, 62.0 | 62.0 |
| `developer​Name` | String | Developer name of the procedure plan definition. | Small, 62.0 | 62.0 |
| `error` | [Procedure Plan Generic Error](./connect_responses_procedure_plan_generic_error.htm.md "Output representation of the error details related to the procedure plan definitions.")[] | Details of the error encountered during the processing of the API request. | Small, 62.0 | 62.0 |
| `name` | String | Name of the procedure plan definition. | Small, 62.0 | 62.0 |
| `primary​Object` | String | Object that’s associated with the procedure plan definition. | Small, 62.0 | 62.0 |
| `procedurePlan​Definition​Versions` | [Procedure Plan Definition Version](./connect_responses_procedure_plan_definition_version_output.htm.md "Output representation of the version details of a procedure plan definition.")[] | Details of the versions of a procedure plan definition. | Small, 62.0 | 62.0 |
| `processType` | String | Business processes that's specified that requires a procedure plan for each sObject and definition. | Small, 63.0 | 63.0 |
| `recordId` | String | ID of the procedure plan definition record. | Small, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
