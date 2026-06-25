---
page_id: connect_requests_expression_set_custom_element_step.htm
title: Expression Set Custom Element Step Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_custom_element_step.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-06-25
---

# Expression Set Custom Element Step Input

Input representation of a custom element step in an expression
set.

Root XML tag
:   `<ExpressionSetCustomElementStepInput>`

JSON example
:   ```
     "customElement": {
                "parameters": [
                  {
                    "input": true,
                    "name": "Divisor",
                    "output": false,
                    "value": "v1"
                  },
                  {
                    "input": true,
                    "name": "Dividend",
                    "output": false,
                    "value": "v2"
                  },
                  {
                    "input": false,
                    "name": "Answer",
                    "output": true,
                    "value": "v3"
                  }
                ]
              },
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `parameters` | [Expression Set Custom Element Parameter Input](./connect_requests_expression_set_custom_element_parameter.htm.md "Input representation of a custom element parameter in an expression set.")[] | List of parameters in a custom element. | Required | 58.0 |
