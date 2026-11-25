---
page_id: connect-requests-procedure-plan-evaluation-input
title: Procedure Plan Evaluation Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-procedure-plan-evaluation-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-requests
legacy_page_id: connect_requests_procedure_plan_evaluation_input.htm
fetched_at: 2026-11-25
---

# Procedure Plan Evaluation Input

Input representation of the details used to evaluate a procedure plan definition.

## JSON Example

This example shows a sample request to evaluate a procedure plan definition by using a primary object.

```
  {
    "idList": ["a01DU000000BylcYAC"], 
    "evaluationDate": "2024-07-08T10:15:30.000Z",
    "processType": "Default", 
    "sectionType": ["PricingProcedure"], 
    "subSectionType": ["Revenue"] 
  }
```

This example shows a sample request to evaluate a procedure plan definition by using a definition name.

```
  {
    "evaluationDate": "2024-07-08T10:15:30.000Z",
    "processType": "Default", 
    "sectionType": ["PricingProcedure"], 
    "subSectionType": ["Revenue"] 
  }
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `evaluationDate` | String | Date when the evaluation is applicable. This property value must be within the date range when the procedure plan definition is effective. | Required | 62.0 |
| `idList` | String[] | List of record IDs of the procedure plan definitions to be evaluated. | Required only if you’re invoking the [Procedure Plan Evaluation By Object (POST) API](./connect-resources-evaluate-procedure-plan-definition-by-object.md). | 62.0 |
| `processType` | String | Specifies the business processes that need a procedure plan for each sObject and definition. Valid values based on the available are `Billing`, `DRO`, `DeepClone`, `ProductDiscovery`, or `Revenue Cloud`. These values can be used based on the available license. If unspecified, the value is set to `Default`. If a procedure plan definition exist in the org with `processType` value as `null`, modify the value to `Default`. | Optional | 63.0 |
| `sectionType` | String[] | Name of section to be evaluated. Valid values are `PricingProcedure`, `ProductDiscoveryProcedure`, `ProductQualificationProcedure`, `PricingDiscoveryProcedure`, `DiscountSpreadServiceProcedure`, `RatingProcedure`, `Custom`, or `RatingDiscoveryProcedure`. | Optional | 62.0 |
| `subSectionType` | String[] | Name of subsection to be evaluated. | Optional | 62.0 |
| `subType` | String | Specifies the vertical or cloud-specific subclassification for the procedure plan definition. | Optional | 68.0 |

The combination of the `sectionType` and `subSectionType` property values must be unique for every procedure plan version.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-procedure-plan-evaluation-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
