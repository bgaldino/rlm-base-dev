---
page_id: connect_responses_facet_value.htm
title: Facet Value
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_facet_value.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_responses.htm
fetched_at: 2026-06-09
---

# Facet Value

Output representation of the facet values found in the search result.

JSON example
:   ```
          "values": [
            {
              "displayName": "1080p Built-in Display",
              "nameOrId": "1080p Built-in Display"
            },
            {
              "displayName": "2k Built-in Display",
              "nameOrId": "2k Built-in Display"
            },
            {
              "displayName": "4k Built-in Display",
              "nameOrId": "4k Built-in Display"
            }
          ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `display​Name` | String | Display name of the facet value. | Small, 63.0 | 63.0 |
| `nameOr​Id` | String | ID or the internal name of the facet value. | Small, 63.0 | 63.0 |
