---
page_id: connect_requests_index_configuration_collection_input.htm
title: Index Configuration Collection Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_index_configuration_collection_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-06-09
---

# Index Configuration Collection Input

Input representation of the collection of index configurations.

JSON example
:   ```
    {
      "correlationId": "8545b5aa-f3e6-429a-8f21-9cc4ce50b1d7",
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
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `correlationId` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Optional | 62.0 |
    | `index​Configurations` | [Index Configuration Input](./connect_requests_index_configuration_input.htm.md "Input representation of the request to persist the index configuration.")[] | List of index configurations. | Required | 62.0 |
