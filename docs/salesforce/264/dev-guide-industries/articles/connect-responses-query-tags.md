---
page_id: connect-responses-query-tags
title: Query Tags
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-query-tags.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-responses
legacy_page_id: connect_responses_query_tags.htm
fetched_at: 2026-11-25
---

# Query Tags

Output representation of query tags result.

**Sample Response**

: 

```
{
                "tagValue": {
                    "Industry": {
                        "contextDataPathBuilder": {
                            "pathTokens": [
                                "6ba44bdce01b138f7cfdf9c7ab414312bf76f4b75362e47adb6ab368714fb5bf",
                                "001SB00000M9i21YAB"
                            ]
                        },
                        "dmlStatus": "CREATED",
                        "nodeLevelTag": false,
                        "tagPath": {
                            "pathTokens": []
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextDataPathBuilder` | Map<String, Object> | Indicates whether the query operation is complete | Small, 59.0 | 59.0 |
| `pathTokens` | String [] | List of paths indicating the tag data path. | Small, 59.0 | 59.0 |
| `dmlStatus` | String | DML status of the tag value. | Small, 59.0 | 59.0 |
| `nodeLevelTag` | Boolean | Indicates if the tag is at the node level `true`) or not (`false`. | Small, 59.0 | 59.0 |
| `tagPath` | Map<String, Object> | The path to the tag containing a list of paths indicating the tag path. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-query-tags.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
