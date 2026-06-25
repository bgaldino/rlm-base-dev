---
page_id: connect_resources_update_context_attribute.htm
title: Context Attribute (PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_update_context_attribute.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: runtime_context_intance_management.htm
fetched_at: 2026-06-25
---

# Context Attribute (PATCH)

Update attributes of a context record.

Resource
:   ```
    /connect/contexts/attributes
    ```

Example for PATCH
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/contexts/attributes
    ```

Available version
:   59.0

Requires Chatter
:   No

HTTP methods
:   PATCH

Request body for PATCH
:   JSON example
    :   ```
        {
            "contextId": "3729ed60-d16d-41b8-8951-9ad4f6407ad2",
            "nodePathAndAttributes": [
                {
                    "nodePath": {
                        "dataPath": [
                            "TestOrder123"
                        ]
                    },
                    "attributes": [
                        {
                            "attributeName": "Status",
                            "attributeValue": "DISPATCHED"
                        }
                    ]
                }
            ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `updateContextAttributesInput` | Object | Input object for updating context attributes. | Required | 59.0 |
:   ![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

    #### Note

    When a context definition is mapped to Account and a field is mapped to `Account.RecordType.Name`, updating the RecordType's ID
    does not update the mapped field. This is because updating the RecordType ID does not
    cause updates to other fields of the RecordType record.

Response body for PATCH
:   [Context
    Output](./connect_responses_context_output.htm.md "Output Representation of attributes associated with defined context.")
