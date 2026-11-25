---
page_id: actions-obj-delete-context-cache
title: Delete Context Cache Action
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/actions-obj-delete-context-cache.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-invocable-actions-parent
legacy_page_id: actions_obj_delete_context_cache.htm
fetched_at: 2026-11-25
---

# Delete Context Cache Action

Delete the specified context instance from the in-memory context cache using the provided context ID. This action removes the cached data maintained by the context cache service without performing any database write operations.

This action is available in API version 63.0 and later.

## Special Access Rules

Available in Developer, Enterprise, Professional, and Unlimited editions for Industries clouds where Context Service is enabled.

## Supported REST HTTP Methods

**URI:** `/services/data/vXX.X/actions/standard/deleteContextCache`

Where `XX.X` is the latest API version.

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where `TOKEN` is a variable.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `contextId` | string | Required. ID of the context instance. |

## Outputs

None.

## Example

**POST**

: 

This sample request is for the Delete Context Cache action.

```
{
  "inputs": [
    {
      "contextId": "0000000a07da09100251752497651022c35b6150a4d04cd6a84bf1a0439cc609"
    }
  ]
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/actions-obj-delete-context-cache.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
