---
page_id: connect_responses_setting_metadata_output.htm
title: Setting Metadata
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_setting_metadata_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Setting Metadata

Output representation of the metadata associated with a setting.

JSON example
:   ```
      "metadata": {
        "activeLanguages": [
          "en_US"
        ]
      }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `active​Languages` | String[] | List of active languages in an org. | Small, 63.0 | 63.0 |
