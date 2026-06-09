---
page_id: connect_responses_procedure_plan_generic_output.htm
title: Procedure Plan Generic
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_procedure_plan_generic_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Procedure Plan Generic

Output representation of the details of the created procedure plan definition
record.

JSON example
:   This example shows a sample response of the details of a procedure plan definition
    record, created by using the Procedure Plan Definitions (POST)
    API.

    ```
      {
       "isSuccess":true,
       "recordId":"1FNDU00000000EX4AY"
      }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | [Procedure Plan Generic Error](./connect_responses_procedure_plan_generic_error.htm.md "Output representation of the error details related to the procedure plan definitions.")[] | Details of the error encountered during the processing of the API request. | Small, 62.0 | 62.0 |
| `isSuccess` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `recordId` | String | ID of the created procedure plan definition record. | Small, 62.0 | 62.0 |
