---
page_id: connect_responses_expression_set_aggregation_step_output.htm
title: Expression Set Aggregation Step
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_expression_set_aggregation_step_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Expression Set Aggregation Step

Output representation of the expression set aggregation
    step.

- 
- 
- 
- 

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `aggergated​Parameter` | String | Expression set version variable that’s present on the right side of the aggregation step. | Small, 58.0 | 58.0 |
| `aggregate​Function` | String | Aggregation function of the expression set.Valid values are: `Avg` `Max` `Min` `Sum` | Small, 58.0 | 58.0 |
| `expression` | String | Expression that’s present on the left side of the aggregation step. | Small, 58.0 | 58.0 |
