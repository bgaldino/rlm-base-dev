---
page_id: connect-responses-index-setting-output
title: Index Setting
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-index-setting-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_index_setting_output.htm
fetched_at: 2026-11-25
---

# Index Setting

Output representation of the retrieved index settings.

## JSON Example

```
{
  "errors": [],
  "metadata": {
    "activeLanguages": ["en_US","ja","es","nl_NL"]
  },
  "setting": {
    "defaultLanguage": "en_US",
    "id": "1JySG0000000GUb0AM",
    "supportedLanguages": ["en_US","ja","es","nl_NL"]
  },
  "statusCode": "200"
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Error Output](./connect-responses-epc-error-output.md)[] | List of errors, if any. | Small, 63.0 | 63.0 |
| `metadata` | [Setting Metadata](./connect-responses-setting-metadata-output.md)[] | Metadata associated with the setting. | Small, 63.0 | 63.0 |
| `setting` | [Setting](./connect-responses-setting-output.md)[] | Setting that’s used in indexing and maintained for an org. | Small, 63.0 | 63.0 |
| `status​Code` | String | Code that indicates the status of the request. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-index-setting-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
