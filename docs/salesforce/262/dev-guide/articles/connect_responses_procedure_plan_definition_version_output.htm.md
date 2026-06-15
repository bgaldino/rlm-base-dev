---
page_id: connect_responses_procedure_plan_definition_version_output.htm
title: Procedure Plan Definition Version
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_procedure_plan_definition_version_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Procedure Plan Definition Version

Output representation of the version details of a procedure plan definition.

JSON example
:   ```
                "procedurePlanDefinitionVersions": [
                 {
                   "active": false,
                   "developerName": "sample_test",
                   "effectiveFrom": "2024-07-09T00:00:00.000Z",
                   "contextDefinition": "SalesTransactionContext__stdctx",
                   "procedurePlanSections": [],
                   "rank": 1,
                   "readContextMapping": "ProductDiscoveryContextMapping",
                   "recordId": "1CvZ60000008OIaKAM",
                   "success": true,
                   "processType": "Default"
                 }
               ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `active` | Boolean | Indicates whether the procedure plan definition version is active (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `context​Definition` | String | Context definition that’s associated with the procedure plan definition version. | Small, 62.0 | 62.0 |
| `developer​Name` | String | Developer name of the procedure plan definition version. | Small, 62.0 | 62.0 |
| `effectiveFrom` | String | Date and time from when the procedure plan definition version is effective. | Small, 62.0 | 62.0 |
| `effectiveTo` | String | Date and time until when the procedure plan definition version is effective. | Small, 62.0 | 62.0 |
| `error` | [Procedure Plan Generic Error](./connect_responses_procedure_plan_generic_error.htm.md "Output representation of the error details related to the procedure plan definitions.")[] | Details of the error encountered during the processing of the API request. | Small, 62.0 | 62.0 |
| `inheritedFrom` | String | Name of the template the procedure plan definition is extended from. | Small, 62.0 | 62.0 |
| `procedure​PlanSections` | [Procedure Plan Section](./connect_responses_procedure_plan_section_output.htm.md "Output representation of the details of a procedure plan section.")[] | List of sections of the procedure plan definition that you can organize in any order. Each section must include a procedure or a set of procedures to be executed for a specific criteria. | Small, 62.0 | 62.0 |
| `processType` | String | Business processes that's specified that requires a procedure plan for each sObject and definition. | Small, 64.0 | 64.0 |
| `rank` | Integer | Rank or the order of sequence to follow for the processing of the procedure plan definition version. | Small, 62.0 | 62.0 |
| `readContext​Mapping` | String | Mapping that’s used to read data from the mapped object and populate the context definition. | Small, 62.0 | 62.0 |
| `recordId` | String | ID of the procedure plan definition version record. | Small, 62.0 | 62.0 |
| `saveContext​Mapping` | String | Mapping that’s used to save data from the context definition and populate the mapped object. | Small, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
