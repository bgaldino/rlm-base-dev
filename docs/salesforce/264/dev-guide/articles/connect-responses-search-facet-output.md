---
page_id: connect-responses-search-facet-output
title: Search Facet
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-search-facet-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_search_facet_output.htm
fetched_at: 2026-11-25
---

# Search Facet

Output representation of the details of the faceted search.

## JSON Example

```
  "facets":[
    {
      "attributeType": "ProductStandard",
      "displayName": "Product Type",
      "displayRank": 1,
      "displayType": "MultiSelect",
      "nameOrId": "Type",
      "values": [
        {
          "displayName": "Simple",
          "nameOrId": "Simple",
          "productCount": 9
        }
      ]
    },
    {
      "attributeType": "ProductStandard",
      "displayName": "Active",
      "displayRank": 2,
      "displayType": "MultiSelect",
      "nameOrId": "IsActive",
      "values": [
        {
          "displayName": "true",
          "nameOrId": "true",
          "productCount": 47
        }
      ]
    }
  ]
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `attribute​Type` | String | Search attribute type of the facet. | Small, 63.0 | 63.0 |
| `display​Name` | String | Display name of the facet. | Small, 63.0 | 63.0 |
| `display​Rank` | Integer | Display rank of the facet. | Small, 63.0 | 63.0 |
| `display​Type` | String | Display type of the face. | Small, 63.0 | 63.0 |
| `nameOr​Id` | String | Facet name or ID. Reserved for internal use. | Small, 63.0 | 63.0 |
| `values` | [Facet Value](./connect-responses-facet-value-output.md)[] | Values of the facet found in the search result. Sorted by display name in alphabetical order. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-search-facet-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
