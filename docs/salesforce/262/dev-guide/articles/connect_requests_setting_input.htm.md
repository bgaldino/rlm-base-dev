---
page_id: connect_requests_setting_input.htm
title: Setting Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_setting_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-06-09
---

# Setting Input

Input representation of the details of the index setting.

JSON example
:   ```
        "setting" : {
            "supportedLanguages" : ["en_US","ja","es","nl_NL"],
            "defaultLanguage" : "en_US"
       }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `default​Language` | String | Default language for the API. | Required | 63.0 |
    | `supported​Languages` | String[] | List of supported language locales for indexing. | Required | 63.0 |
