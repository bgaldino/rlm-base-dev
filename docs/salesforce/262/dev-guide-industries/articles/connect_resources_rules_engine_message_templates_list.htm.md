---
page_id: connect_resources_rules_engine_message_templates_list.htm
title: Explainability Message Templates (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_rules_engine_message_templates_list.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_explainer_bre_resources.htm
fetched_at: 2026-06-25
---

# Explainability Message Templates (GET)

Retrieves a list of explainability message templates that matches
the given search parameters.

Resource
:   ```
    /connect/business-rules/explainability/message-templates
    ```

Resource Example
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect
    /business-rules/explainability/message-templates?messageType=Passed
    ```

Available version
:   56.0

Requires Chatter
:   No

HTTP methods
:   GET

Request parameters for GET
:   ![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

    #### Note

    You must specify at least one parameter as part of the GET request.

    | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `isDefault` | Boolean | Specifies whether the message in the explainability message template for an expression set step type is default (`true`) or not (`false`). | Optional | 56.0 |
    | `messageType` | String | The message defined for a step when the step result is either passed or failed. | Optional | 56.0 |
    | `searchKey` | String | The keyword used to retrieve the list of templates. | Optional | 56.0 |
    | `stepType` | String | The type of expression set step element. Pass one of these values for this field:   - Calculation - Branch - Condition - Decision Matrix Lookup - Decision Table Lookup - Aggregation - Sub Expression - Business Element | Optional | 56.0 |

Response body for GET
:   [Message Templates List](./connect_responses_message_templates_list_output.htm.md "Output representation of the list of explainability message templates.")
