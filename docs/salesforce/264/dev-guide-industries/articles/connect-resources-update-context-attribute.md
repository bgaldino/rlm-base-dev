---
page_id: connect-resources-update-context-attribute
title: Context Attribute (PATCH)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-update-context-attribute.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: runtime-context-intance-management
legacy_page_id: connect_resources_update_context_attribute.htm
fetched_at: 2026-11-25
---

# Context Attribute (PATCH)

Update attributes of a context record.

## Resource

```
/connect/contexts/attributes
```

## Example for PATCH

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/contexts/attributes
```

{yourInstance} is the domain name of your Salesforce instance.

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

[Context Output](./connect-responses-context-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-update-context-attribute.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
