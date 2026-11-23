---
page_id: connect_responses_context_attribute.htm
title: Context Attribute Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_attribute.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-11-23
---

# Context Attribute Output

Output representation of the context attribute.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `attributeTags` | [Context Attribute Tag](./connect_responses_context_attribute_tag.htm.md "Output representation of context attribute tag.")[] | List of context attribute tags. | Small, 59.0 | 59.0 |
| `contextAttributeId` | String | ID of this context attribute. | Small, 59.0 | 59.0 |
| `dataType` | String | Data type of the context attribute. | Small, 59.0 | 59.0 |
| `domainSet` | String | Comma separated node names referenced by this attribute. | Small, 59.0 | 59.0 |
| `fieldType` | String | Field type of the attribute. | Small, 59.0 | 59.0 |
| `isKey` | Boolean | Specifies if it used for transposable feature (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Specifies if the operation is success (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `isValue` | Boolean | Specifies if it used for transposable (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `name` | String | Name of the attribute. | Small, 59.0 | 59.0 |
| `parentNodeId` | String | ID of (parent) context node. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_attribute.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
