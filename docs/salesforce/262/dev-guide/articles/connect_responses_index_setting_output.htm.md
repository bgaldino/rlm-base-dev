---
page_id: connect_responses_index_setting_output.htm
title: Index Setting
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_index_setting_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Index Setting

Output representation of the retrieved index settings.

JSON example
:   ```
    {
      "errors": [],
      "metadata": {
        "activeLanguages": ["en_US","ja","es","nl_NL"]
      },
      "setting": {
        "defaultLanguage": "en_US",
        "id": "1JySG0000000GUb0AM",
        "supportedLanguages": ["en_US","ja","es","nl_NL"]
      },
      "statusCode": "200"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Error Output](./connect_responses_epc_error_output.htm.md "Output representation of the error details.")[] | List of errors, if any. | Small, 63.0 | 63.0 |
| `metadata` | [Setting Metadata](./connect_responses_setting_metadata_output.htm.md "Output representation of the metadata associated with a setting.")[] | Metadata associated with the setting. | Small, 63.0 | 63.0 |
| `setting` | [Setting](./connect_responses_setting_output.htm.md "Output representation of the setting that’s used in indexing.")[] | Setting that’s used in indexing and maintained for an org. | Small, 63.0 | 63.0 |
| `status​Code` | String | Code that indicates the status of the request. | Small, 63.0 | 63.0 |
