---
page_id: connect_resources_context_tag.htm
title: Context Tag (GET, POST, PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_tag.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_tag_managament.htm
fetched_at: 2026-06-25
---

# Context Tag (GET, POST, PATCH)

Query, create, and update context tag.

Resource
:   ```
    /connect/context-definitions/${contextDefinitionId}/context-tags
    ```

Example for GET
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}/context-tags
    ```

Example for POST
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}/context-tags
    ```

Example for PATCH
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}/context-tags
    ```

Available version
:   59.0

Requires Chatter
:   No

HTTP methods
:   GET, POST, PATCH

Response body for GET
:   [Context Tag List Output](./connect_responses_context_tag_list.htm.md "Output representation of list of context tags.")

    ![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

    #### Note

    When the `includeReferencedDefinitionTag` query
    parameter is set to `true` in a GET request, the
    response will include the name of the context tag in the format `ContextDeveloperName.tagName`.

Request body for POST
:   JSON example
    :   ```
        {
            "contextTags": [
                {
                    "name": "Attribute_Tag",
                    "contextAttributeId": "11nxx000001hOozAAE"
                },
                {
                    "name": "Node_Tag",
                    "contextNodeId": "11oxx000001G9D2AAK"
                }
            ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `contextAttributeId` | String | ID of the (parent) context attribute. | Required | 59.0 |
        | `contextNodeId` | String | ID of the (parent) context node. | Required | 59.0 |
        | `contextTagId` | String | ID of this Context tag. Required only for update. | Optional | 59.0 |
        | `name` | String | Name of the context tag. | Required | 59.0 |

Response body for POST
:   [Context Tag List Output](./connect_responses_context_tag_list.htm.md "Output representation of list of context tags.")

Request body for PATCH
:   JSON example
    :   ```
        {
            "contextTags": [
                {
                    "name": "Updated_ATag",
                    "contextTagId": "11kxx00000ZzcDpAAJ"
                }
            ]
        }
        ```

Response body for PATCH
:   [Context Tag List Output](./connect_responses_context_tag_list.htm.md "Output representation of list of context tags.")
