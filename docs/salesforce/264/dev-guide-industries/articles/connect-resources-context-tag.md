---
page_id: connect-resources-context-tag
title: Context Tag (GET, POST, PATCH)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-tag.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-tag-managament
legacy_page_id: connect_resources_context_tag.htm
fetched_at: 2026-11-25
---

# Context Tag (GET, POST, PATCH)

Query, create, and update context tag.

## Resource

```
/connect/context-definitions/{contextDefinitionId}/context-tags
```

The {contextDefinitionId} parameter is the ID of the context definition.

## Example for GET

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-definitions/{contextDefinitionId}/context-tags
```

{yourInstance} is the domain name of your Salesforce instance.

## Example for POST

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-definitions/{contextDefinitionId}/context-tags
```

## Example for PATCH

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-definitions/{contextDefinitionId}/context-tags
```

## Available Version

59.0

## Requires Chatter

No

## HTTP Methods

GET, POST, PATCH

## Response Body for GET

[Context Tag List Output](./connect-responses-context-tag-list.md)

**Note:**

When the `includeReferencedDefinitionTag` query parameter is set to `true` in a GET request, the response will include the name of the context tag in the format `ContextDeveloperName.tagName`.

## Request Body for POST

### JSON Example

```
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

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextAttributeId` | String | ID of the (parent) context attribute. | Required | 59.0 |
| `contextNodeId` | String | ID of the (parent) context node. | Required | 59.0 |
| `contextTagId` | String | ID of this Context tag. Required only for update. | Optional | 59.0 |
| `name` | String | Name of the context tag. | Required | 59.0 |

## Response Body for POST

[Context Tag List Output](./connect-responses-context-tag-list.md)

## Request Body for PATCH

### JSON Example

```
{
    "contextTags": [
        {
            "name": "Updated_ATag",
            "contextTagId": "11kxx00000ZzcDpAAJ"
        }
    ]
}
```

## Response Body for PATCH

[Context Tag List Output](./connect-responses-context-tag-list.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-tag.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
