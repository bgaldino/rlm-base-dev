---
page_id: connect_responses_fields_info_output.htm
title: Fields Info
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_fields_info_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Fields Info

Output representation of the metadata fields in an object.

JSON example
:   ```
            "fields": [
              {
                "dataType": "text",
                "isFacetableConfigurable": true,
                "isSearchableConfigurable": false,
                "label": "Product Name",
                "name": "Name",
                "type": "Standard"
              },
              {
                "dataType": "multilinetext",
                "isFacetableConfigurable": false,
                "isSearchableConfigurable": true,
                "label": "Product Description",
                "name": "Description",
                "type": "Standard"
              }
            ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `customField​Id` | String | ID of the custom field. | Small, 62.0 | 62.0 |
| `dataType` | String | Type of data. | Small, 62.0 | 62.0 |
| `is​Configurable` | Boolean | Reserved for internal use. | Small, 62.0 | 62.0 |
| `isFacetable​Configurable` | Boolean | Indicates whether the field is facetable (`true`) or not (`false`). | Small, 63.0 | Small, 63.0 |
| `isSearchable​Configurable` | Boolean | Indicates whether the field is searchable (`true`) or not (`false`). | Small, 63.0 | Small, 63.0 |
| `label` | String | Label of the object field. | Small, 62.0 | 62.0 |
| `name` | String | Name of the object field. | Small, 62.0 | 62.0 |
| `type` | String | Type of the object field. | Small, 62.0 | 62.0 |
