---
page_id: connect_requests_calculation_procedure_step_input.htm
title: Calculation Procedure Step Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_calculation_procedure_step_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_requests.htm
fetched_at: 2026-06-25
---

# Calculation Procedure Step Input

Input representation for the expression set version
steps.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

This API has been deprecated as of API version 55.0.
In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `calculationMatrixId` | String | The ID of the decision matrix record. | Optional Note Note This field is required when the step type is `MatrixLookup`. | 53.0 |
    | `childStepId` | String[] | The IDs of the child steps in the parent expression set version record step. | Optional | 53.0 |
    | `conditionsExpressionText` | String | The user-defined expression text used in a condition step. | Optional | 53.0 |
    | `conditionsUiFormattedText` | String | Additional information required to render the condition expression text. For example, when the current step has a subset of `childStepIds` that is marked to bypass. Specify `"conditionsUiFormattedText":"{\"bypass\":[\"0mqx000000000f6AAA\"]}"` in the field to enable navigation outside the branch. | Optional | 53.0 |
    | `description` | String | The description of the expression set version record step. | Optional | 53.0 |
    | `formulaExpressionText` | String | The formula used in a calculation step. | Optional | 53.0 |
    | `formulaUiFormattedText` | String | Reserved for future use. | Optional | 53.0 |
    | `id` | String | The ID of the expression set version record step. | Required Note Note This field is required for the update request. | 53.0 |
    | `inputVariablesFormatText` | String | The input variables in JSON format required to execute an expression set version record step. | Required | 53.0 |
    | `isResultIncluded` | Boolean | Indicates whether the result of a step execution is returned to the user. The default is `false`. | Optional | 53.0 |
    | `name` | String | The name of the expression set version record step. | Optional | 53.0 |
    | `outputVariablesFormatText` | String | The output variables in JSON format returned by an expression set version record step. | Required | 53.0 |
    | `outputVariablesMappingText` | String | The mapping between the output variable of a step and the input variable for a sub-calculation procedure version record or a sub-decision matrix record. | Optional Note Note This field is required when the step type is `MatrixLookup` or `ReferenceProcedure`. | 53.0 |
    | `referenceCalculationProcedureId` | String | The ID of the sub-calculation procedure version record. | Optional Note Note This field is required when the step type is `ReferenceProcedure`. | 53.0 |
    | `returnMessageValueSet` | String | User-configured messages for the result of the current step. | Optional | 53.0 |
    | `stage` | String | Specify whether the expression set version step is a calculation or an aggregation. Note Note In version 53.0 and later, only calculation is supported. | Required | 53.0 |
    | `stepType` | String | Specify the step type in the expression set version. Possible values are:  - `Condition` - `Calculation` - `MatrixLookup` - `ReferenceProcedure` - `Branch` - `ConditionalGroup` | Required | 53.0 |
