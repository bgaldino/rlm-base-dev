---
page_id: connect_responses_leaner_query_tags_result.htm
title: Leaner Query Tags Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_leaner_query_tags_result.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-06-25
---

# Leaner Query Tags Result

Output representation of the leaner query tags result. The result includes compact tag
data mapped to tag names and a shared list of record IDs.

JSON example
:   ```
    {
      "contextId": "0000000s07fm061002917633740427233ff03037a8fe48048696667781ec824c",
      "isSuccess": true,
      "errorMessage": null,
      "recordIds": [
        "001xx000003GYiBAAW",
        "003xx000004WhFpAAK",
        "003xx000004WhFqAAK",
        "003xx000004WhFoAAK"
      ],
      "queryResultLeanerRepresentation": {
        "Contact_FirstName": [
          {
            "nodeLevelTag": false,
            "recordIdIndexesForPath": [
              0,
              1
            ],
            "tagValue": "Carole"
          },
          {
            "nodeLevelTag": false,
            "recordIdIndexesForPath": [
              0,
              2
            ],
            "tagValue": "Jon"
          },
          {
            "nodeLevelTag": false,
            "recordIdIndexesForPath": [
              0,
              3
            ],
            "tagValue": "Geoff"
          }
        ]
      }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextId` | String | ID of context to be queried. | Small, 66.0 | 66.0 |
| `errorMessage` | String | Error message when `isSuccess` is false. | Small, 66.0 | 66.0 |
| `isSuccess` | Boolean | Indicates whether the query was successful (`true`) or not (`true`). | Small, 66.0 | 66.0 |
| `queryResult​LeanerRepresentation` | [Context Tag Data Leaner](./connect_responses_context_tag_data_leaner.htm.md "Output representation of the leaner context tag data. It stores only the metadata required to reconstruct tag values and the index references instead of full path strings.") | Map of tag name and list of lean tag data. Each entry contains tag values and compact indexes for record path construction. | Small, 66.0 | 66.0 |
| `recordIds` | String[] | List of all record IDs present in the context that are included in the tag result. | Small, 66.0 | 66.0 |
