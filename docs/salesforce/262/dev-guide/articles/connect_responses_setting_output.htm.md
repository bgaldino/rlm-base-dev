---
page_id: connect_responses_setting_output.htm
title: Setting
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_setting_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Setting

Output representation of the setting that’s used in indexing.

JSON example
:   ```
      "setting": {
        "defaultLanguage": "en_US",
        "id": "1JySG0000000GUb0AM",
        "supportedLanguages": ["en_US","ja","es","nl_NL"]
      }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `default​Language` | String | Default language for the API. | Small, 63.0 | 63.0 |
| `id` | String | ID of the setting. | Small, 63.0 | 63.0 |
| `supported​Languages` | String[] | List of supported language locales for indexing. | Small, 63.0 | 63.0 |
