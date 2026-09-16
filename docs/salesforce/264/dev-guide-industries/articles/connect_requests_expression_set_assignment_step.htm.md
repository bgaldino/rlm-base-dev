---
page_id: connect_requests_expression_set_assignment_step.htm
title: Expression Set Assignment Step Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_assignment_step.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Expression Set Assignment Step Input

Input representation of an assignment step in an expression
    set.

**Root XML tag**

: `<ExpressionSetAssignmentStepInput>`

**JSON example**

: 

```
"assignment" : {
            "assignedParameter" : "b",
            "expression" : "100"
          }
```

**Properties**

: 

                    

                    

                    

                    

                    

                  

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `assigned​Parameter` | String | Expression set version variable that’s present on the right side of the calculation step. | Required | 58.0 |
| `expression` | String | Expression that’s present on the left side of the calculation step. | Required | 58.0 |
