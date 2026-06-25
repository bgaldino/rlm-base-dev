---
page_id: connect_resources_decision_table_definition_details.htm
title: Decision Table Definitions (DELETE, GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_decision_table_definition_details.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_table_resources.htm
fetched_at: 2026-06-25
---

# Decision Table Definitions (DELETE, GET)

Get details of a decision table definition. Delete a decision table
definition associated with a decision table.

Resource
:   ```
    /connect/business-rules/decision-table/definitions/${decisionTableId}
    ```

Resource Example
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/business-rules/decision-table/definitions/0lDxx00000002Ur
    ```

Available version
:   58.0

Requires Chatter
:   No

HTTP methods
:   DELETE, GET

Response body for DELETE
:   [Decision Table
    Output](./connect_responses_decision_table_output.htm.md "Output representation of the decision table details.")

Response body for GET
:   [Decision Table Output](./connect_responses_decision_table_output.htm.md "Output representation of the decision table details.")
