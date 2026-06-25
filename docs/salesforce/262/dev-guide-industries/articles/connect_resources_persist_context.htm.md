---
page_id: connect_resources_persist_context.htm
title: Persist Context (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_persist_context.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: persistence_context_management.htm
fetched_at: 2026-06-25
---

# Persist Context (POST)

Persist a context by passing the context ID.

Resource
:   ```
    /connect/contexts/persist-records
    ```

Example for POST
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/contexts/persist-records
    ```

Available version
:   59.0

Requires Chatter
:   No

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "contextPersistInput": {
            "contextId": "384fdcef-36e2-4bbb-82ed-2e7bc4e670c7",
            "targetMappingId": "11jxx0000004Q83AAE"
          }
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `contextPersistInput` | Object | Contains contextId and targetMappingId for persisting context. | Required | 59.0 |

JSON example
:   ```
    {
      "contextId": "384fdcef-36e2-4bbb-82ed-2e7bc4e670c7",
      "targetMappingId": "11jxx0000004Q83AAE"
    }
    ```

Response body for POST
:   [Persist
    Context Output](./connect_responses_persist_context_output.htm.md "Output Representation to persist context data.")

    ![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

    #### Note

    When updating reference fields within a context and attempting to persist the
    context, changes to the reference field itself may not be persisted. This is because
    reference fields point to related entities, and the persist operation primarily
    focuses on the attributes of the main entity within the context.

    For example, if you have an Order context with a reference field to an Account,
    updating the Account reference within the Order context and then calling the persist
    API may not save the updated Account reference. Other attributes of the Order might
    be persisted, but the relationship to the Account might not be.
