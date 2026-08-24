---
page_id: connect_responses_context_attribute.htm
title: Context Attribute Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_attribute.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Attribute Output

Output representation of the context attribute.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `attributeTags` | [Context Attribute Tag](./connect_responses_context_attribute_tag.htm.md)[] | List of context attribute tags. | Small, 59.0 | 59.0 |
| `contextAttributeId` | String | ID of this context attribute. | Small, 59.0 | 59.0 |
| `dataType` | String | Data type of the context attribute. | Small, 59.0 | 59.0 |
| `domainSet` | String | Comma separated node names referenced by this attribute. | Small, 59.0 | 59.0 |
| `fieldType` | String | Field type of the attribute. | Small, 59.0 | 59.0 |
| `isKey` | Boolean | Specifies if it used for transposable feature (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Specifies if the operation is success (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `isValue` | Boolean | Specifies if it used for transposable (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `name` | String | Name of the attribute. | Small, 59.0 | 59.0 |
| `parentNodeId` | String | ID of (parent) context node. | Small, 59.0 | 59.0 |
