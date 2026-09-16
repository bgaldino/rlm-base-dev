---
page_id: connect_responses_procedure_plan_evaluation_result.htm
title: Procedure Plan Evaluation Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_procedure_plan_evaluation_result.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Procedure Plan Evaluation Result

Output representation of the evaluation result of a procedure plan
    definition.

        
          

**JSON example**

          
: 
            

```
    "result":{
    "contextDefinition":"11ODU00000008Sw2AI",
    "procedurePlanSections":[]
  }
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `context​Definition` | String | Context definition that’s associated with the procedure plan evaluation. | Small, 62.0 | 62.0 |
| `procedure​PlanSections` | [Procedure Plan Section Evaluation Runtime](./connect_responses_procedure_plan_section_evaluation_runtime.htm.md)[] | Results from the procedure plan evaluation. | Small, 62.0 | 62.0 |
