---
page_id: connect_responses_guided_selection_search_term_output.htm
title: Guided Selection Search Term
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_guided_selection_search_term_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_responses.htm
fetched_at: 2026-06-09
---

# Guided Selection Search Term

Output representation of the search term details for a guided selection.

JSON example
:   ```
    {
      "searchTerms": [
        {
          "term": "IPhone",
          "tags": [
            "deviceType",
            "mobile"
          ]
        },
        {
          "term": "4GB",
          "tags": [
            "RAM"
          ]
        },
        {
          "term": "64GB",
          "tags": [
            "Storage"
          ]
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `tags` | String[] | Search term tags for the guided selection. | Small, 62.0 | 62.0 |
| `term` | String | Search term value for the guided selection. | Small, 62.0 | 62.0 |
