---
page_id: connect_responses_expression_set_des_token_mapping.htm
title: Expression Set DES Token Mapping
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_expression_set_des_token_mapping.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_responses.htm
fetched_at: 2026-06-25
---

# Expression Set DES Token Mapping

Output representation of the DES token mapping in an expression set
version step.

JSON example
:   ```
    "passedMessageTokenMappings": [
    {
    "expressionSetMessageToken": "price",
    "resourceReference": "DM1__Price"
    }
    ],
    "failedMessageTokenMappings": [
    {
    "expressionSetMessageToken": "model",
    "resourceReference": "Model"
    }
    ],

    "noResultTokenMappings": [
    {
    "expressionSetMessageToken": "year",
    "resourceReference": "Year"
    }
    ]
    ```

Properties
:   | Name | Type | Description | Filter Group and Version | Available Version |
    | --- | --- | --- | --- | --- |
    | `resource​Reference` | String | Name of the expression set resource that’s mapped to a token, such as Variable, Constant, or FiledAlias. | Small, 59.0 | 59.0 |
    | `expressionSet​MessageToken` | String | Name of the explainability message template token. | Small, 59.0 | 59.0 |
