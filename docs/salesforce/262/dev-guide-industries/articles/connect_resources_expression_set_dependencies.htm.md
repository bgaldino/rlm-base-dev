---
page_id: connect_resources_expression_set_dependencies.htm
title: Expression Set Version Dependencies (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_expression_set_dependencies.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_resources.htm
fetched_at: 2026-06-25
---

# Expression Set Version Dependencies (GET)

Retrieve expression set version dependencies.

Resource
:   ```
    /connect/business-rules/expression-set/version/${expressionSetVersionId}/dependencies
    ```

Resource Example
:   ```
    https://yourInstance.salesforce.com/services/data/v58.0/connect/business-rules/expression-set/version/9QARN000000016v4AA/dependencies
    ```

Available version
:   58.0

Requires Chatter
:   No

HTTP methods
:   GET

Response body for GET
:   [Expression Set Version Dependency](./connect_responses_expression_set_version_dependency_output.htm.md "Output representation for the expression set version dependency.")
