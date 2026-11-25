---
page_id: connect-resources-evaluate-procedure-plan-definition-by-object
title: Procedure Plan Evaluation By Object (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-evaluate-procedure-plan-definition-by-object.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-business-apis-rest-references
legacy_page_id: connect_resources_evaluate_procedure_plan_definition_by_object.htm
fetched_at: 2026-11-25
---

# Procedure Plan Evaluation By Object (POST)

Evaluate a procedure plan definition based on a primary object to check for prerequisites such as usage type and context mapping details.

## Resource

```
/connect/procedure-plan-definitions/evaluate
```

## Resource Example

```
https://{yourInstance}.salesforce.com​/services/data​/v68.0/connect/​procedure-plan-definitions/​evaluate
```

## Available Version

62.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

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

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `evaluationDate` | String | Date when the evaluation is applicable. This property value must be within the date range when the procedure plan definition is effective. | Required | 62.0 |
| `idList` | String[] | List of record IDs of the procedure plan definitions to be evaluated. | Required only if you’re invoking the [Procedure Plan Evaluation By Object (POST) API](./connect-resources-evaluate-procedure-plan-definition-by-object.md). | 62.0 |
| `processType` | String | Specifies the business processes that need a procedure plan for each sObject and definition. Valid values based on the available are `Billing`, `DRO`, `DeepClone`, `ProductDiscovery`, or `Revenue Cloud`. These values can be used based on the available license. If unspecified, the value is set to `Default`. If a procedure plan definition exist in the org with `processType` value as `null`, modify the value to `Default`. | Optional | 63.0 |
| `sectionType` | String[] | Name of section to be evaluated. Valid values are `PricingProcedure`, `ProductDiscoveryProcedure`, `ProductQualificationProcedure`, `PricingDiscoveryProcedure`, `DiscountSpreadServiceProcedure`, `RatingProcedure`, `Custom`, or `RatingDiscoveryProcedure`. | Optional | 62.0 |
| `subSectionType` | String[] | Name of subsection to be evaluated. | Optional | 62.0 |
| `subType` | String | Specifies the vertical or cloud-specific subclassification for the procedure plan definition. | Optional | 68.0 |

The combination of the `sectionType` and `subSectionType` property values must be unique for every procedure plan version.

## Response Body for POST

[Procedure Plan Evaluation Response](./connect-responses-procedure-plan-evaluation-response.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-evaluate-procedure-plan-definition-by-object.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
