---
page_id: connect-responses-object-info-output
title: Object Info
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-object-info-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_object_info_output.htm
fetched_at: 2026-11-25
---

# Object Info

Output representation of the object details along with its fields.

## JSON Example

```
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
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `fields` | [Fields Info](./connect-responses-fields-info-output.md)[] | Fields of the object. | Small, 62.0 | 62.0 |
| `name` | String | Name of the object. | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-object-info-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
