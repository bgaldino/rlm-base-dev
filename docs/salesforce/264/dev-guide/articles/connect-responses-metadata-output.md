---
page_id: connect-responses-metadata-output
title: Metadata
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-metadata-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_metadata_output.htm
fetched_at: 2026-11-25
---

# Metadata

Output representation of the metadata details for objects.

## JSON Example

```
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

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `objectInfos` | [Object Info](./connect-responses-object-info-output.md)[] | Metadata details for objects. | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-metadata-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
