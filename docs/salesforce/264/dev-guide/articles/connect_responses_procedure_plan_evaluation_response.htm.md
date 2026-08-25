---
page_id: connect_responses_procedure_plan_evaluation_response.htm
title: Procedure Plan Evaluation Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_procedure_plan_evaluation_response.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Procedure Plan Evaluation Response

Output representation of the evaluation details of a procedure plan
    definition.

        
          

**JSON example**

          
: 
            

```
  {
  "isSuccess":true,
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
  }
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorMessage` | String | Message indicating the error details, if any. | Small, 62.0 | 62.0 |
| `isSuccess` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `procedure​PlanDefinition​Name` | String | Name of the procedure plan definition. | Small, 62.0 | 62.0 |
| `procedure​Plan​Evaluations` | [Procedure Plan Evaluation](./connect_responses_procedure_plan_evaluation.htm.md)[] | Evaluation details of the procedure plan. | Small, 62.0 | 62.0 |
