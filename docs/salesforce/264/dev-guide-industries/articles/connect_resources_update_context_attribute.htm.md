---
page_id: connect_resources_update_context_attribute.htm
title: Context Attribute (PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_update_context_attribute.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: runtime_context_intance_management.htm
fetched_at: 2026-11-23
---

# Context Attribute (PATCH)

Update attributes of a context record.

## Resource

```
/connect/contexts/attributes
```

## Example for PATCH

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/contexts/attributes
```

## Available Version

59.0

## Requires Chatter

No

## HTTP Methods

PATCH

## Request Body for PATCH

### JSON Example

```
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

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `updateContextAttributesInput` | Object | Input object for updating context attributes. | Required | 59.0 |

## Response Body for PATCH

[Context
Output](./connect_responses_context_output.htm.md "Output Representation of attributes associated with defined context.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_update_context_attribute.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
