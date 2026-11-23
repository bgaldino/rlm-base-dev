---
page_id: connect_responses_facet_value_output.htm
title: Facet Value
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_facet_value_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-11-23
---

# Facet Value

Output representation of the facet values found in the search result.

## JSON Example

```
      "values": [
        {
          "displayName": "Simple",
          "nameOrId": "Simple",
          "productCount": 9
        }
      ]
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `display​Name` | String | Display name of the facet value. | Small, 63.0 | 63.0 |
| `nameOr​Id` | String | Facet value name or ID. Reserved for internal use. | Small, 63.0 | 63.0 |
| `product​Count` |  | Number of products in the search result that match the facet value. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_facet_value_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
