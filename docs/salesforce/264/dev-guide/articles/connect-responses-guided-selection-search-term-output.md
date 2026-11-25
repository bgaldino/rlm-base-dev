---
page_id: connect-responses-guided-selection-search-term-output
title: Guided Selection Search Term
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-guided-selection-search-term-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-api-responses
legacy_page_id: connect_responses_guided_selection_search_term_output.htm
fetched_at: 2026-11-25
---

# Guided Selection Search Term

Output representation of the search term details for a guided selection.

## JSON Example

```
{
  "searchTerms": [
    {
      "term": "IPhone",
      "tags": [
        "deviceType",
        "mobile"
      ]
    },
    {
      "term": "4GB",
      "tags": [
        "RAM"
      ]
    },
    {
      "term": "64GB",
      "tags": [
        "Storage"
      ]
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `tags` | String[] | Search term tags for the guided selection. | Small, 62.0 | 62.0 |
| `term` | String | Search term value for the guided selection. | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-guided-selection-search-term-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
