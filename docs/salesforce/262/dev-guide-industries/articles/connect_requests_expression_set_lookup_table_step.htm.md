---
page_id: connect_requests_expression_set_lookup_table_step.htm
title: Expression Set Lookup Table Step Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_lookup_table_step.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-06-25
---

# Expression Set Lookup Table Step Input

Input representation of a lookup table step in an expression
set.

Root XML tag
:   `<ExpressionSetLookupTableStepInput>`

JSON example
:   ```
                  "lookupTable": {
                    "lookupTableName": "DM_for_test",
                    "type": "DecisionMatrix"
                  }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `lookup​TableName` | String | Decision matrix or decision table name that’s used in the lookup table step. | Required | 58.0 |
    | `type` | String | Lookup table type of the expression set. Valid values are:   - `DecisionMatrix` - `DecisionTable` | Required | 58.0 |
