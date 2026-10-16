---
page_id: connect_requests_expression_set_aggregation_step.htm
title: Expression Set Aggregation Step Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_aggregation_step.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Expression Set Aggregation Step Input

Input representation of an aggregation step in an expression
    set.

**Root XML tag**

: `<ExpressionSetAggregationStepInput>`

**JSON example**

: 

```
"aggregation" : {
"aggergatedParameter" : "v1",
"aggregateFunction" : "Sum",
"expression" : "SUM ( v2 )"
}
```

**Properties**

: 

                    

                    

                    

                    

                    

                  

- 
- 
- 
- 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `aggergated​Parameter` | String | Expression set version variable that’s present on the right side of the aggregation step. | Required | 58.0 |
| `aggregate​Function` | String | Aggregation function of the expression set.Valid values are: `Avg` `Max` `Min` `Sum` | Required | 58.0 |
| `expression` | String | Expression that’s present on the left side of the aggregation step. | Required | 58.0 |
