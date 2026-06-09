---
page_id: connect_requests_procedure_plan_evaluation_input.htm
title: Procedure Plan Evaluation Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_procedure_plan_evaluation_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_requests.htm
fetched_at: 2026-06-09
---

# Procedure Plan Evaluation Input

Input representation of the details used to evaluate a procedure plan
definition.

JSON example
:   This example shows a sample request to evaluate a
    procedure plan definition by using a primary
    object.

    ```
      {
        "idList": ["a01DU000000BylcYAC"], 
        "evaluationDate": "2024-07-08T10:15:30.000Z",
        "processType": "Default", 
        "sectionType": ["PricingProcedure"], 
        "subSectionType": ["Revenue"] 
      }
    ```
:   This example shows a sample request to
    evaluate a procedure plan definition by using a definition
    name.

    ```
      {
        "evaluationDate": "2024-07-08T10:15:30.000Z",
        "processType": "Default", 
        "sectionType": ["PricingProcedure"], 
        "subSectionType": ["Revenue"] 
      }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `evaluationDate` | String | Date when the evaluation is applicable. This property value must be within the date range when the procedure plan definition is effective. | Required | 62.0 |
    | `idList` | String[] | List of record IDs of the procedure plan definitions to be evaluated. | Required only if you’re invoking the [Procedure Plan Evaluation By Object (POST) API](./connect_resources_evaluate_procedure_plan_definition_by_object.htm.md "Evaluate a procedure plan definition based on a primary object to check for prerequisites such as usage type and context mapping details."). | 62.0 |
    | `processType` | String | Specifies the business processes that need a procedure plan for each sObject and definition. Valid values based on the available are:   - `Billing` - `DRO` - `DeepClone` - `ProductDiscovery` - `Revenue Cloud`   These values can be used based on the available license. If unspecified, the value is set to `Default`.  If a procedure plan definition exist in the org with `processType` value as `null`, modify the value to `Default`. | Optional | 63.0 |
    | `sectionType` | String[] | Name of section to be evaluated. Valid values are:  - `PricingProcedure` - `ProductDiscoveryProcedure` - `ProductQualificationProcedure` - `PricingDiscoveryProcedure` - `DiscountSpreadServiceProcedure` - `RatingProcedure` - `Custom` - `RatingDiscoveryProcedure` | Optional | 62.0 |
    | `subSectionType` | String[] | Name of subsection to be evaluated. | Optional | 62.0 |

    The combination of the `sectionType` and
    `subSectionType` property values must be unique
    for every procedure plan version.
