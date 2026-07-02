---
page_id: connect_requests_expression_set_sub_expression_step.htm
title: Expression Set SubExpression Step Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_sub_expression_step.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-06-25
---

# Expression Set SubExpression Step Input

Input representation of a subexpression step in an expression
set.

Root XML tag
:   `<ExpressionSetSubExpressionStepInput>`

JSON example
:   ```
                  "subExpression": {
                    "expressionSet": "EPC_ExpressionSet_NoVersions"
                  }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `expression​Set` | String | Expression set name that’s used in the subexpression set step. | Required | 58.0 |
