---
page_id: connect_responses_document_template_parent.htm
title: Document Template Parent
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_document_template_parent.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Document Template Parent

Output representation of the document template parent record.

              

              

              

              

              

            

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `hasMoreVersions` | Boolean | Indicates whether the document template parent record has more draft and archive versions (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `isActive` | Boolean | Indicates whether the the document template parent record is currently active (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `lastModifiedDate` | String | Last modified date of the document template parent record. | Small, 60.0 | 60.0 |
| `name` | String | Name of the document template parent record. | Small, 60.0 | 60.0 |
| `namespace` | String | Namespace associated with the document template parent record. | Small, 60.0 | 60.0 |
| `type` | String | Type of the document template parent record. | Small, 60.0 | 60.0 |
| `usageType` | String | Usage type of the document template parent record. | Small, 60.0 | 60.0 |
| `versions` | [Document Template Child](./connect_responses_document_template_child.htm.md)[] | List of versions associated to the document template parent record. | Small, 60.0 | 60.0 |
