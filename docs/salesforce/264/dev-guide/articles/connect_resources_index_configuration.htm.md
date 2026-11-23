---
page_id: connect_resources_index_configuration.htm
title: Index Configuration Collection (GET, PUT)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_index_configuration.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-11-23
---

# Index Configuration Collection (GET, PUT)

Retrieve the saved index configurations. Additionally, you can persist the index configuration.

**Resource**

```
/connect/pcm/index/configurations
```

**Resource Example**

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/index/configurations
```

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/index/configurations?includeMetadata=false&fieldTypes=Standard,Custom
```

**Available Version:** 62.0

**HTTP Methods:** GET, PUT

**Request Parameters for GET**

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `correlationId` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Optional | 62.0 |
| `field​Types` | String[] | Filters and returns only the persisted index configurations, based on the index configuration type specified in the query parameters. The supported types of filters are `STANDARD`, `CUSTOM`, `ProductDynamicAttribute`, `ProductAttributeDefinitionStandard`, or `ProductAttributeDefinitionCustom`. | Optional | 62.0 |
| `include​Metadata` | Boolean | Indicates whether to include metadata (`true`) or not (`false`). | Optional | 62.0 |

**Response Body for GET:** [Index Configuration Collection](./connect_responses_index_configuration_collection_output.htm.md "Output representation of the collection of index configuration details.")

**Request Body for PUT**

**JSON Example**

```
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

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `correlationId` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Optional | 62.0 |
| `index​Configurations` | [Index Configuration Input](./connect_requests_index_configuration_input.htm.md "Input representation of the request to persist the index configuration.")[] | List of index configurations. | Required | 62.0 |

**Response Body for PUT:** [Index Configurations Update](./connect_responses_index_configurations_update_output.htm.md "Output representation of the updated index configuration.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_index_configuration.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
