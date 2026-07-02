---
page_id: connect_responses_index_error_output.htm
title: Index Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_index_error_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Index Error

Output representation of the error details related to an index.

JSON example
:   ```
      "indexErrorDetails": {
        "errorFileId": "069xx0000004C92AAE",
        "indexCreatedDate": "2024-10-03T05:24:18.000Z",
        "indexErrorsCount": 1,
        "indexLastUpdatedDate": "2024-10-03T05:27:00.000Z",
        "itemLevelErrorsCount": 1
      }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error​FileId` | String | ID of the exported error file that contains the index errors. | Small, 63.0 | 63.0 |
| `indexCreated​Date` | String | Date on which the index was created. | Small, 63.0 | 63.0 |
| `index​ErrorsCount` | Integer | Number of index-level errors. | Small, 63.0 | 63.0 |
| `indexLast​UpdatedDate` | String | Date on which the index was last updated. | Small, 63.0 | 63.0 |
| `itemLevel​ErrorsCount` | Integer | Number of item-level errors. | Small, 63.0 | 63.0 |
