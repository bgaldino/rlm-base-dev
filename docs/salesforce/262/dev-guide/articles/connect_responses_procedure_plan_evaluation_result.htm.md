---
page_id: connect_responses_procedure_plan_evaluation_result.htm
title: Procedure Plan Evaluation Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_procedure_plan_evaluation_result.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Procedure Plan Evaluation Result

Output representation of the evaluation result of a procedure plan
definition.

JSON example
:   ```
        "result":{
        "contextDefinition":"11ODU00000008Sw2AI",
        "procedurePlanSections":[]
      }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `context​Definition` | String | Context definition that’s associated with the procedure plan evaluation. | Small, 62.0 | 62.0 |
| `procedure​PlanSections` | [Procedure Plan Section Evaluation Runtime](./connect_responses_procedure_plan_section_evaluation_runtime.htm.md "Output representation of the results from the procedure plan evaluation.")[] | Results from the procedure plan evaluation. | Small, 62.0 | 62.0 |
