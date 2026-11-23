---
page_id: connect_resources_get_index_settings.htm
title: Index Setting (GET, PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_index_settings.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-11-23
---

# Index Setting (GET, PATCH)

Fetch and update settings related to indexing and search.

**Resource**

```
/connect/pcm/index/setting
```

**Resource Example**

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/index/setting
```

**Available Version:** 63.0

**HTTP Methods:** GET, PATCH

**Response Body for GET:** [Index Setting Results](./connect_responses_index_setting_output.htm.md "Output representation of the retrieved index settings.")

**Request Body for PATCH**

**JSON Example**

```
{
    "setting" : {
        "supportedLanguages" : ["en_US","ja","es","nl_NL"],
        "defaultLanguage" : "en_US",
        "productsGrouping": "GROUPING_VARIATION"
   }
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `setting` | [Setting Input](./connect_requests_setting_input.htm.md "Input representation of the details of the index setting.")[] | Object containing the setting-related details. | Required | 63.0 |

**Request Parameters for PATCH**

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `settingId` | String | ID of the setting to update the details for. | Required | 63.0 |

**Response Body for PATCH:** [Index Setting Update](./connect_responses_index_setting_patch_output.htm.md "Output representation of the details of the updated index setting.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_index_settings.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
