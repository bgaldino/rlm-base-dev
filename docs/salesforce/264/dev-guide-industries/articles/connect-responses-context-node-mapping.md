---
page_id: connect-responses-context-node-mapping
title: Context Node Mapping Output
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-node-mapping.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-responses
legacy_page_id: connect_responses_context_node_mapping.htm
fetched_at: 2026-11-25
---

# Context Node Mapping Output

Output representation of the context node mapping.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `attributeMappings` | [Context Attribute Mapping](./connect-responses-context-attribute-mapping.md)[] | List of the context attribute mappings. | Small, 59.0 | 59.0 |
| `contextMappingID` | String | ID of the context mapping. | Small, 59.0 | 59.0 |
| `contextNodeID` | String | ID of the context node. | Small, 59.0 | 59.0 |
| `contextNodeMappingID` | String | ID of this context node mapping. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Specifies if the operation is successful (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `mappedContext​NodeId` | String | Node ID in the source context definition. | Small, 61.0 | 61.0 |
| `sObjectName` | String | SObject name. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-node-mapping.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
