---
page_id: connect-requests-procedure-plan-criterion-input
title: Procedure Plan Criterion Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-procedure-plan-criterion-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-requests
legacy_page_id: connect_requests_procedure_plan_criterion_input.htm
fetched_at: 2026-11-25
---

# Procedure Plan Criterion Input

Input representation of the details of a procedure plan criterion.

## JSON Example

```
         "procedurePlanCriterion": [
            {
              "conditionSequence": 1,
              "fieldObject": "BillingCountry",
              "fieldPath": "BillingCountry",
              "literalValue": "test",
              "operator": "Equals",
              "dataType": "Text"
            },
            {
              "conditionSequence": 2,
              "fieldObject": "BillingPostalCode",
              "fieldPath": "BillingPostalCode",
              "literalValue": "sample",
              "operator": "Equals",
              "dataType": "Text"
            },
            {
              "conditionSequence": 3,
              "fieldObject": "LastActivityDate",
              "fieldPath": "LastActivityDate",
              "literalValue": "2024-07-14",
              "operator": "LessThan",
              "dataType": "Date"
            }
          ]
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `condition​Sequence` | Integer | Sequence to be followed to process the conditions defined in the procedure plan option. This property value must be unique within a procedure plan option. | Required | 62.0 |
| `dataType` | String | Data type of the field from the selected object. | Required | 62.0 |
| `field​Object` | String | Value of the object field that’s used to resolve the procedure plan option. This property value must belong to the primary object that’s associated with the procedure plan definition, at a maximum two levels up in the hierarchy. | Required | 62.0 |
| `fieldPath` | String | Path of the field that’s used in a procedure in relation to the object that the field belongs to. The field path must end with the object field that’s associated with the procedure plan criterion. | Required | 62.0 |
| `literal​Value` | String | User-defined value that’s compared to the value of the sObject field value. | Optional | 62.0 |
| `operator` | String | Operator that’s used by the procedure plan criterion. | Required | 62.0 |
| `recordId` | String | ID of the procedure plan criterion record. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-procedure-plan-criterion-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
