---
page_id: connect_responses_setting_output.htm
title: Setting
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_setting_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-11-23
---

# Setting

Output representation of the setting that’s used in indexing.

## JSON Example

```
  "setting": {
    "defaultLanguage": "en_US",
    "id": "1JySG0000000GUb0AM",
    "supportedLanguages": ["en_US","ja","es","nl_NL"]
  }
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `default​Language` | String | Default language for the API. | Small, 63.0 | 63.0 |
| `id` | String | ID of the setting. | Small, 63.0 | 63.0 |
| `supported​Languages` | String[] | List of supported language locales for indexing. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_setting_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
