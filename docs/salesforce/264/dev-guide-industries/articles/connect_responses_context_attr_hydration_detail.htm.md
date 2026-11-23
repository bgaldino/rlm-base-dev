---
page_id: connect_responses_context_attr_hydration_detail.htm
title: Context Attribute Hydration Detail
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_attr_hydration_detail.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-11-23
---

# Context Attribute Hydration Detail

Output representation of context attribute hydration detail.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `childDetails` | [Context Attribute Hydration Detail](#connect_responses_context_attr_hydration_detail "Output representation of context attribute hydration detail.")[] | List of parent context attribute hydration detail. | Small, 59.0 | 59.0 |
| `contextAttrHydrationDetailId` | String | ID of this context attribute hydration detail record. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Indicates whether the operation is successful (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `mappedAttributeDataTypeInfo` | [Mapped Attribute Data Type](./connect_responses_mapped_attribute_data_type_info.htm.md "Output representation of the context attribute mapping data type information.")[] | Data type of the attribute mapped field. | Small, 59.0 | 59.0 |
| `parentMappingAttributeId` | String | ID of the parent context attribute mapping record. | Small, 59.0 | 59.0 |
| `queryAttribute` | String | Query attribute. | Small, 59.0 | 59.0 |
| `sObjectDomain` | String | sObject domain. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_attr_hydration_detail.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
