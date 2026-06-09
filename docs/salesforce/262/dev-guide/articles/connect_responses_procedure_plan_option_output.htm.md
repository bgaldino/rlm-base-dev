---
page_id: connect_responses_procedure_plan_option_output.htm
title: Procedure Plan Option
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_procedure_plan_option_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Procedure Plan Option

Output representation of the details of a procedure plan option.

JSON example
:   ```
                     "procedurePlanOptions": [
                       {
                         "expressionSetApiName": "Revenue_Mgmt_Default_Pricing_Procedure",
                         "expressionSetDefinition": "9QAZ60000004ECOOA2",
                         "expressionSetLabel": "Revenue Management Default Pricing Procedure",
                         "isSuccess": true,
                         "logic": "1 AND 2 AND 3",
                         "primaryObject": "Account",
                         "priority": 1,
                         "procedurePlanCriterion": [
                           {
                             "conditionSequence": 1,
                             "dataType": "Text",
                             "fieldObject": "BillingCountry",
                             "fieldPath": "BillingCountry",
                             "isSuccess": true,
                             "literalValue": "test",
                             "operator": "Equals",
                             "recordId": "1FiZ60000004C9cKAE"
                            },
                            {
                             "conditionSequence": 2,
                             "dataType": "Text",
                             "fieldObject": "BillingPostalCode",
                             "fieldPath": "BillingPostalCode",
                             "isSuccess": true,
                             "literalValue": "pramit",
                             "operator": "Equals",
                             "recordId": "1FiZ60000004C9dKAE"
                             },
                             {
                               "conditionSequence": 3,
                               "dataType": "Date",
                               "fieldObject": "LastActivityDate",
                               "fieldPath": "LastActivityDate",
                               "isSuccess": true,
                               "literalValue": "2024-07-14",
                               "operator": "LessThan",
                               "recordId": "1FiZ60000004C9eKAE"
                              }
                            ],
                           "recordId": "1FYZ6000000000fOAA",
                           "saveContextMapping": "AssetToSalesTransactionMapping"
                            }
                          ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | [Procedure Plan Generic Error](./connect_responses_procedure_plan_generic_error.htm.md "Output representation of the error details related to the procedure plan definitions.")[] | Details of the error encountered during the processing of the API request. | Small, 62.0 | 62.0 |
| `expression​SetApi​Name` | String | API name of the expression set. | Small, 62.0 | 62.0 |
| `expression​Set​Definition` | String | Expression set definition that’s associated with this procedure plan option record. | Small, 62.0 | 62.0 |
| `expression​SetLabel` | String | Label of the expression set that’s associated with this procedure plan option record. | Small, 62.0 | 62.0 |
| `isSuccess` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `logic` | String | Computation logic for the conditions applied to a procedure plan option. | Small, 62.0 | 62.0 |
| `primary​Object` | String | Source object that’s used to create a procedure with rule-based criteria. | Small, 62.0 | 62.0 |
| `priority` | Integer | Priority for the specified criteria. | Small, 62.0 | 62.0 |
| `procedure​PlanCriterion` | [Procedure Plan Criterion](./connect_responses_procedure_plan_criterion_output.htm.md "Output representation of the details of a procedure plan criterion.")[] | Details of the rule-based criteria for the procedure. | Small, 62.0 | 62.0 |
| `readContext​Mapping` | String | Mapping that’s used to read from the mapped object and populate the context definition. | Small, 62.0 | 62.0 |
| `recordId` | String | ID of the procedure plan option record. | Small, 62.0 | 62.0 |
| `saveContext​Mapping` | String | Mapping that’s used to save data from the context definition and populate the mapped object. | Small, 62.0 | 62.0 |
