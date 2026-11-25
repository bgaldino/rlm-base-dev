---
page_id: connect-requests-context-attributes-input
title: Context Attributes Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-context-attributes-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-requests
legacy_page_id: connect_requests_context_attributes_input.htm
fetched_at: 2026-11-25
---

# Context Attributes Input

Input representation of context attribute.

## JSON Example

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

## Properties

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-context-attributes-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
