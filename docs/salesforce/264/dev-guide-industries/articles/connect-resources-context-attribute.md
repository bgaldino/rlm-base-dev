---
page_id: connect-resources-context-attribute
title: Context Attribute (POST, PATCH)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-attribute.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-attribute-management
legacy_page_id: connect_resources_context_attribute.htm
fetched_at: 2026-11-25
---

# Context Attribute (POST, PATCH)

Create a list of context attributes.

## Resource

```
/connect/context-nodes/{contextNodeId}/context-attributes
```

The {contextNodeId} parameter is the ID of the context node.

## Example for POST

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-nodes/{contextNodeId}/context-attributes
```

{yourInstance} is the domain name of your Salesforce instance.

## Example for PATCH

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-nodes/{contextNodeId}/context-attributes
```

## Available Version

59.0

## Requires Chatter

No

## HTTP Methods

POST, PATCH

## Request Body for POST

### JSON Example

```
{
    "contextAttributes": [
        {
            "dataType": "STRING",
            "fieldType": "INPUT",
            "name": "Attribute_5",
            "tags": {
                "contextTags": [
                    {
                        "name": "Attribute_5_Tag"
                    }
                ]
            }
        },
        {
            "dataType": "NUMBER",
            "fieldType": "OUTPUT",
            "name": "Attribute_6"
        }
    ]
}
```

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextAttributeId` | String | ID of the attribute. | Required | 59.0 |
| `dataType` | String | Data type of the attribute. | Required | 59.0 |
| `domainSet` | String | Comma separated node names referenced by this attribute. | Optional | 59.0 |
| `fieldType` | String | Field type of the attribute. | Required | 59.0 |
| `isKey` | Boolean | Specifies if it used for transposable feature (`true`) or not (`false`). | Optional | 59.0 |
| `isValue` | Boolean | Specifies if it used for transposable feature (`true`) or not (`false`). | Optional | 59.0 |
| `name` | String | Name of the attribute. | Required | 59.0 |
| `tags` | [Context Tag Input](./connect-requests-context-tag-input.md)[] | List of tags for the attribute. | Optional | 59.0 |

## Response Body for POST

[Context Attribute List](./connect-responses-context-attribute-list.md)

## Request Body for PATCH

### JSON Example

```
{
    "contextAttributes": [
        {
            "name": "Attribute_5_Updated",
            "contextAttributeId": "11nxx000001hOvRAAU"
        },
        {
            "name": "Attribute_6_Updated",
            "contextAttributeId": "11nxx000001hOvSAAU"
        }
    ]
}
```

## Response Body for PATCH

[Context Attribute List](./connect-responses-context-attribute-list.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-attribute.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
