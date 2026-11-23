---
page_id: connect_resources_context_tag.htm
title: Context Tag (GET, POST, PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_tag.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_tag_managament.htm
fetched_at: 2026-11-23
---

# Context Tag (GET, POST, PATCH)

Query, create, and update context tag.

## Resource

```
/connect/context-definitions/contextDefinitionId/context-tags
```

## Example for GET

```
https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/contextDefinitionId/context-tags
```

## Example for POST

```
https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/contextDefinitionId/context-tags
```

## Example for PATCH

```
https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/contextDefinitionId/context-tags
```

## Available Version

59.0

## Requires Chatter

No

## HTTP Methods

GET, POST, PATCH

## Response Body for GET

[Context
Tag List Output](./connect_responses_context_tag_list.htm.md "Output representation of list of context tags.")

![Note](/docs/resources/img/en-us/264.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

When the `includeReferencedDefinitionTag` query parameter is set to `true` in a GET request, the response will include the name
of the context tag in the format `ContextDeveloperName.tagName`.

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

[Context Tag List Output](./connect_responses_context_tag_list.htm.md "Output representation of list of context tags.")

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

[Context Tag List Output](./connect_responses_context_tag_list.htm.md "Output representation of list of context tags.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_tag.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
