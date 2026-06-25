---
page_id: connect_requests_context_attribute_input.htm
title: Context Attribute Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_attribute_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_overview.htm
fetched_at: 2026-06-25
---

# Context Attribute Input

Input representation for updating context attribute.

JSON example
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
