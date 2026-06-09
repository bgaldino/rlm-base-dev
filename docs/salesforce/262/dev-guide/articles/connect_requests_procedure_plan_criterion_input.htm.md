---
page_id: connect_requests_procedure_plan_criterion_input.htm
title: Procedure Plan Criterion Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_procedure_plan_criterion_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_requests.htm
fetched_at: 2026-06-09
---

# Procedure Plan Criterion Input

Input representation of the details of a procedure plan criterion.

JSON example
:   ```
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

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `condition​Sequence` | Integer | Sequence to be followed to process the conditions defined in the procedure plan option.  This property value must be unique within a procedure plan option. | Required | 62.0 |
    | `dataType` | String | Data type of the field from the selected object. | Required | 62.0 |
    | `field​Object` | String | Value of the object field that’s used to resolve the procedure plan option.  This property value must belong to the primary object that’s associated with the procedure plan definition, at a maximum two levels up in the hierarchy. | Required | 62.0 |
    | `fieldPath` | String | Path of the field that’s used in a procedure in relation to the object that the field belongs to.  The field path must end with the object field that’s associated with the procedure plan criterion. | Required | 62.0 |
    | `literal​Value` | String | User-defined value that’s compared to the value of the sObject field value. | Optional | 62.0 |
    | `operator` | String | Operator that’s used by the procedure plan criterion. | Required | 62.0 |
    | `recordId` | String | ID of the procedure plan criterion record. | Required | 62.0 |
