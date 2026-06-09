---
page_id: connect_responses_index_configurations_update_output.htm
title: Index Configurations Update
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_index_configurations_update_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Index Configurations Update

Output representation of the updated index configuration.

JSON example
:   ```
    {
      "correlationId": "8545b5aa-f3e6-429a-8f21-9cc4ce50b1d7",
      "errors": [],
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
      ],
      "statusCode": "200"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `correlationId` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Small, 62.0 | 62.0 |
| `errors` | [Error Output](./connect_responses_epc_error_output.htm.md "Output representation of the error details.")[] | List of errors, if any. | Small, 62.0 | 62.0 |
| `index​Configurations` | [Index Configuration Field](./connect_responses_index_configuration_field_output.htm.md "Output representation of the details of the index-configured field.")[] | Details of the index-configured fields. | Small, 62.0 | 62.0 |
| `status​Code` | String | Code that indicates the status of the request. | Small, 62.0 | 62.0 |
