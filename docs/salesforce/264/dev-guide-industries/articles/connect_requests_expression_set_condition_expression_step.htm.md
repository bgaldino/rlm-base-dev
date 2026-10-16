---
page_id: connect_requests_expression_set_condition_expression_step.htm
title: Expression Set Condition Expression Step
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_condition_expression_step.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Expression Set Condition Expression Step

Input representation of an expression set condition
    step.

**Root XML tag**

: `<ExpressionSetConditionExpressionStepInput>`

**JSON example**

: 
            

```
"conditionExpression": {
                "expression": "productName == 'iPhone' && City == 'Los Angeles'",
                "resultParameter": "condition_output__1"
              }
```

          

**Properties**

: 

                    

                    

                    

                    

                    

                  

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `expression` | String | Expression that’s defined for the step. | Required | 58.0 |
| `result​Parameter` | String | Expression set version variable associated with the result of the step. | Required | 58.0 |
