---
page_id: connect-responses-index-configuration-collection-output
title: Index Configuration Collection
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-index-configuration-collection-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_index_configuration_collection_output.htm
fetched_at: 2026-11-25
---

# Index Configuration Collection

Output representation of the collection of index configuration details.

## JSON Example

```
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

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `correlationId` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Small, 62.0 | 62.0 |
| `errors` | [Error Output](./connect-responses-epc-error-output.md)[] | List of errors, if any. | Small, 62.0 | 62.0 |
| `index​Configurations` | [Index Configuration Field](./connect-responses-index-configuration-field-output.md)[] | Details of the index-configured fields. | Small, 62.0 | 62.0 |
| `metadata` | [Metadata](./connect-responses-metadata-output.md)[] | Details of the metadata for objects. | Small, 62.0 | 62.0 |
| `statusCode` | String | Code that indicates the status of the request. | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-index-configuration-collection-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
