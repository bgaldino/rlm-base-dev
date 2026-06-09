---
page_id: connect_responses_index_setting_patch_output.htm
title: Index Setting Update
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_index_setting_patch_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Index Setting Update

Output representation of the details of the updated index setting.

JSON example
:   ```
    {
       "setting" : {
            "supportedLanguages" : ["en_US","ja","es","nl_NL"],
            "id": "1JySG0000000GUb0AM",
            "defaultLanguage" : "en_US"
       },
       "errors" : [],
       "statusCode" : "200"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Error Output](./connect_responses_epc_error_output.htm.md "Output representation of the error details.")[] | List of errors, if any. | Small, 63.0 | 63.0 |
| `setting` | [Setting](./connect_responses_setting_output.htm.md "Output representation of the setting that’s used in indexing.")[] | Setting that’s used in indexing and maintained for an org. | Small, 63.0 | 63.0 |
| `statusCode` | String | Code that indicates the status of the API request. | Small, 63.0 | 63.0 |
