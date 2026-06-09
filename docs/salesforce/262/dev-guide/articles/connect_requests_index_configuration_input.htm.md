---
page_id: connect_requests_index_configuration_input.htm
title: Index Configuration Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_index_configuration_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-06-09
---

# Index Configuration Input

Input representation of the request to persist the index configuration.

JSON example
:   ```
      "indexConfigurations": [
        {
          "attributeDefinitionId": "0tjT1000000002bIAA",
          "name": "Color",
          "type": "ProductDynamicAttribute",
          "isSearchable": true
        },
        {
          "attributeFieldId": "00Nxx000001FwnABII",
          "name": "Message__c",
          "type": "Custom",
          "isSearchable": true
        },
        {
          "name": "Code",
          "type": "Standard",
          "isSearchable": true
        },
        {
          "facetDisplayRank": 1,
          "isFacetable": false,
          "isSearchable": true,
          "name": "Family",
          "type": "Standard"
        }
      ]
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `attribute​DefinitionId` | String | ID of the attribute definition. | Required if the `attribute​FieldId`property isn’t specified. | 62.0 |
    | `attribute​FieldId` | String | ID of the attribute field. | Required if the `attribute​DefinitionId`property isn’t specified. | 62.0 |
    | `facet​DisplayRank` | Integer | Sort order for displaying the facets at run time. | Optional | 63.0 |
    | `is​Facetable` | Boolean | Indicates whether the field is facetable (`true`) or not (`false`). | Optional | 63.0 |
    | `is​Searchable` | Boolean | Indicates whether the index-configured field is searchable (`true`) or not (`false`). | Optional | 62.0 |
    | `name` | String | Name of the index-configured field. | Required | 62.0 |
    | `type` | String | Type of the index-configured field. | Required | 62.0 |
