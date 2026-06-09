---
page_id: connect_responses_procedure_plan_evaluation.htm
title: Procedure Plan Evaluation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_procedure_plan_evaluation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Procedure Plan Evaluation

Output representation of the evaluation details of a procedure plan
definition.

JSON example
:   ```
      "procedurePlanEvaluations":[
      {
        "errorMessage":"",
        "id":"a01DU000000BylcYAC",
        "isSuccess":true,
        "primaryObject":"SignallingCustomEvaluation__c",
        "result":{
        "contextDefinition":"11ODU00000008Sw2AI",
        "procedurePlanSections":[]
      }
      }
      ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorMessage` | String | Message indicating the error details, if any. | Small, 62.0 | 62.0 |
| `id` | String | ID of the object used for evaluation. | Small, 62.0 | 62.0 |
| `isSuccess` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `primaryObject` | String | Name of the object used for evaluation. | Small, 62.0 | 62.0 |
| `result` | [Procedure Plan Evaluation Result](./connect_responses_procedure_plan_evaluation_result.htm.md "Output representation of the evaluation result of a procedure plan definition.")[] | Results from the procedure plan evaluation. | Small, 62.0 | 62.0 |
