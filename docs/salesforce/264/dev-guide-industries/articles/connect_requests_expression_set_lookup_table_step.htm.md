---
page_id: connect_requests_expression_set_lookup_table_step.htm
title: Expression Set Lookup Table Step Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_lookup_table_step.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Expression Set Lookup Table Step Input

Input representation of a lookup table step in an expression
    set.

**Root XML tag**

: `<ExpressionSetLookupTableStepInput>`

**JSON example**

: 

```

              "lookupTable": {
                "lookupTableName": "DM_for_test",
                "type": "DecisionMatrix"
              }
```

**Properties**

: 

- 
- 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `lookup​TableName` | String | Decision matrix or decision table name that’s used in the lookup table step. | Required | 58.0 |
| `type` | String | Lookup table type of the expression set.Valid values are: `DecisionMatrix` `DecisionTable` | Required | 58.0 |
