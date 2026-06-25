---
page_id: connect_requests_context_definition_input.htm
title: Context Definition Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_definition_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-06-25
---

# Context Definition Input

Input representation of the context definitions in an expression
set.

Root XML tag
:   `<ContextDefinitionInput>`

JSON example
:   ```
      "contextDefinitionList": {
          "contextDefinitions":[{
          "id":"11Oxx0000006PcLEAU"
          }]
      }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `id` | String | ID of the context definition. | Required | 58.0 |
    | `name` | String | Developer name of the context definition. | Optional | 58.0 |
