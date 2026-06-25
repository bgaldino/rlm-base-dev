---
page_id: connect_resources_bre_guardrail.htm
title: Guardrails (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_guardrail.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_resources.htm
fetched_at: 2026-06-25
---

# Guardrails (GET)

Fetches guardrails from the Business Rules Engine (BRE) to manage rate limits for BRE
components.

Resource
:   ```
    /connect/business-rules/guardrails
    ```

Example POST
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/business-rules/guardrails
    ```

Available version
:   63.0

HTTP methods
:   GET

Request parameters for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `componentNames` | String | BRE component to fetch the guardrails. It contains a comma-separated list of predefined components. Valid component values are:   - `ExpressionSet` - `DecisionTable` - `DecisionMatrix` - `Explainability` - `DynamicRules`  If no values are provided, guardrails for all components accessible to the user are returned. | Optional | 63.0 |
    | `isNotification​Enabled` | Boolean | Indicates whether to return only the guardrails with enabled notifications (`true`) or not (`false`). | Optional | 63.0 |

Response body for GET
:   [BRE Guardrails](./connect_responses_bre_guardrails.htm.md "Output representation of the BRE guardrails for each component.")
