---
page_id: connect_responses_fields_info_output.htm
title: Fields Info
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_fields_info_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-11-23
---

# Fields Info

Output representation of the metadata fields in an object.

## JSON Example

```
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

## Properties

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_fields_info_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
