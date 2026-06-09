---
page_id: connect_responses_index_configuration_collection_output.htm
title: Index Configuration Collection
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_index_configuration_collection_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Index Configuration Collection

Output representation of the collection of index configuration details.

JSON example
:   ```
    {
      "correlationId": "ad960cb6-392d-4d11-bac3-3824baedf67e",
      "errors": [],
      "indexConfigurations": [
        {
          "isSearchable": true,
          "name": "Name",
          "type": "Standard"
        }
      ],
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
      },
      "statusCode": "200"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `correlationId` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Small, 62.0 | 62.0 |
| `errors` | [Error Output](./connect_responses_epc_error_output.htm.md "Output representation of the error details.")[] | List of errors, if any. | Small, 62.0 | 62.0 |
| `index​Configurations` | [Index Configuration Field](./connect_responses_index_configuration_field_output.htm.md "Output representation of the details of the index-configured field.")[] | Details of the index-configured fields. | Small, 62.0 | 62.0 |
| `metadata` | [Metadata](./connect_responses_metadata_output.htm.md "Output representation of the metadata details for objects.")[] | Details of the metadata for objects. | Small, 62.0 | 62.0 |
| `statusCode` | String | Code that indicates the status of the request. | Small, 62.0 | 62.0 |
