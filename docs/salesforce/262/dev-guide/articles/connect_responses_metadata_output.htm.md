---
page_id: connect_responses_metadata_output.htm
title: Metadata
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_metadata_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Metadata

Output representation of the metadata details for objects.

JSON example
:   ```
      "metadata": {
        "objectInfos": [
          {
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
            ],
            "name": "Product2"
          },
          {
            "fields": [
              {
                "dataType": "stringplusclob",
                "label": "Description",
                "name": "Description",
                "type": "ProductAttributeDefinitionStandard"
              },
              {
                "dataType": "text",
                "label": "Name",
                "name": "Name",
                "type": "ProductAttributeDefinitionStandard"
              },
            ],
            "name": "ProductAttributeDefinition"
          }
        ]
      }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `objectInfos` | [Object Info](./connect_responses_object_info_output.htm.md "Output representation of the object details along with its fields.")[] | Metadata details for objects. | Small, 62.0 | 62.0 |
