---
page_id: connect_resources_bre_expression_set_id_delete_get.htm
title: Expression Set (DELETE, GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_expression_set_id_delete_get.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_resources.htm
fetched_at: 2026-06-25
---

# Expression Set (DELETE, GET)

Read or delete expression set for a specified expression set
ID.

Resource
:   ```
    /connect/business-rules/expression-set/${expressionSetId}
    ```

Resource Example
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/business-rules/expression-set/$11Oxx0000006PcLEAU
    ```

Available version
:   58.0

Requires Chatter
:   No

HTTP methods
:   DELETE, GET

Response body for GET
:   [Expression Set Output](./connect_responses_expression_set_output.htm.md "Output representation of the expression set create, update and delete request.")

Response body for DELETE
:   None.
