---
page_id: connect-responses-context-tag-data-leaner
title: Context Tag Data Leaner
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-tag-data-leaner.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-responses
legacy_page_id: connect_responses_context_tag_data_leaner.htm
fetched_at: 2026-11-25
---

# Context Tag Data Leaner

Output representation of the leaner context tag data. It stores only the metadata required to reconstruct tag values and the index references instead of full path strings.

## JSON Example

```
{
  "nodeLevelTag": false,
  "recordIdIndexesForPath": [
    0,
    2
  ],
  "tagValue": "Blue"
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `nodeLevel​Tag` | Boolean | Indicates whether the tag is at node level (`true`) or not. (`false`) | Small, 66.0 | 66.0 |
| `recordId​IndexesForPath` | Integer[] | List of integer indexes referencing the recordIds array to reconstruct the data path.For example, if `recordIds` is [“r4”, “r2”, “r10”, “r1”] and `recordIdIndexesForPath` is [3, 1], the reconstructed path would be contextId/r1/r2 (where r1 is at index 3 and r2 is at index 1). | Small, 66.0 | 66.0 |
| `tagValue` | Object | Value of the tag. For attribute-level tags, this is a primitive value. For node-level tags, this is a map containing nested tag data. | Small, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-tag-data-leaner.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
