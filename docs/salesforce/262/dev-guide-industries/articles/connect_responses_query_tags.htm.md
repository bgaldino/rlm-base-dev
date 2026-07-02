---
page_id: connect_responses_query_tags.htm
title: Query Tags
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_query_tags.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-06-25
---

# Query Tags

Output representation of query tags result.

Sample Response
:   ```
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
