---
page_id: connect-responses-setting-metadata-output
title: Setting Metadata
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-setting-metadata-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_setting_metadata_output.htm
fetched_at: 2026-11-25
---

# Setting Metadata

Output representation of the metadata associated with a setting.

## JSON Example

```
  "metadata": {
    "activeLanguages": [
      "en_US"
    ]
  }
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `active​Languages` | String[] | List of active languages in an org. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-setting-metadata-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
