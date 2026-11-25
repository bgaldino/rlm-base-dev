---
page_id: connect-responses-facet-value
title: Facet Value
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-facet-value.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-api-responses
legacy_page_id: connect_responses_facet_value.htm
fetched_at: 2026-11-25
---

# Facet Value

Output representation of the facet values found in the search result.

## JSON Example

```
      "values": [
        {
          "displayName": "1080p Built-in Display",
          "nameOrId": "1080p Built-in Display"
        },
        {
          "displayName": "2k Built-in Display",
          "nameOrId": "2k Built-in Display"
        },
        {
          "displayName": "4k Built-in Display",
          "nameOrId": "4k Built-in Display"
        }
      ]
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `display​Name` | String | Display name of the facet value. | Small, 63.0 | 63.0 |
| `nameOr​Id` | String | ID or the internal name of the facet value. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-facet-value.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
