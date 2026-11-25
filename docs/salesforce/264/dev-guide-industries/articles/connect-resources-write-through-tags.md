---
page_id: connect-resources-write-through-tags
title: Write Through Tags (PATCH)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-write-through-tags.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: runtime-context-intance-management
legacy_page_id: connect_resources_write_through_tags.htm
fetched_at: 2026-11-25
---

# Write Through Tags (PATCH)

Update Context Attributes through tags.

## Resource

```
/connect/contexts/write-through-tags
```

## Available Version

63.0

## HTTP Methods

PATCH

## Request Body for PATCH

### JSON Example

```
{
    "contextId": "3ec8da809ebd6cef79f685239fb005e8c7cffa075a0d3d7b1d8d17ec22bxxxxd",
    "nodePathAndTagValues": [
        {
            "nodePath": {
                "dataPath": [
                    "001xx000003GbQSAA0"
                ]
            },
            "tagValues": [
                {
                    "tagName": "Name",
                    "tagValue": "updatedAccount"
                },
                {
                    "tagName": "City",
                    "tagValue": "Bangalore"
                }
            ]
        }
    ]
}
```

## Request Parameters for PATCH

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextId` | String | ID of context which will get updated. | Required | 63.0 |
| `nodePath​And​TagValues` | [List<Node​PathAndTag​ValuesInput​Representation>](./connect-requests-node-path-and-tag-values.md) | Node path which needs to update with tag details. | Required | 63.0 |

## Response Body for PATCH

[ContextOutputRepresentation](./connect-responses-context-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-write-through-tags.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
