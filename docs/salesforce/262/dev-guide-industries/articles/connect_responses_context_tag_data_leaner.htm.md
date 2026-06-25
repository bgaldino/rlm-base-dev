---
page_id: connect_responses_context_tag_data_leaner.htm
title: Context Tag Data Leaner
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_tag_data_leaner.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-06-25
---

# Context Tag Data Leaner

Output representation of the leaner context tag data. It stores only the metadata
required to reconstruct tag values and the index references instead of full path
strings.

JSON example
:   ```
    {
      "nodeLevelTag": false,
      "recordIdIndexesForPath": [
        0,
        2
      ],
      "tagValue": "Blue"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `nodeLevel​Tag` | Boolean | Indicates whether the tag is at node level (`true`) or not. (`false`) | Small, 66.0 | 66.0 |
| `recordId​IndexesForPath` | Integer[] | List of integer indexes referencing the recordIds array to reconstruct the data path.For example, if `recordIds` is ["r4", "r2", "r10", "r1"] and `recordIdIndexesForPath` is [3, 1], the reconstructed path would be contextId/r1/r2 (where r1 is at index 3 and r2 is at index 1). | Small, 66.0 | 66.0 |
| `tagValue` | Object | Value of the tag. For attribute-level tags, this is a primitive value. For node-level tags, this is a map containing nested tag data. | Small, 66.0 | 66.0 |
