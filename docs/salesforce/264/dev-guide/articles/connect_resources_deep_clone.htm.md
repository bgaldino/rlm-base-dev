---
page_id: connect_resources_deep_clone.htm
title: Deep Clone (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_deep_clone.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-11-23
---

# Deep Clone (POST)

Copy related records of an object along with the main product record.

**Resource**

```
/connect/pcm/deep-clone
```

**Resource Example**

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/deep-clone
```

**Available Version:** 63.0

**HTTP Methods:** POST

**Request Body for POST**

**JSON Example**

```
{
  "mainRecordId": "01tSG0000028kcSYAQ",
  "mainObjectApiName": "Product2",
  "mainRecordFieldValues": {
    "Name": "New Cloud Storage"
  }
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `mainObject​ApiName` | String | API name of the object. The supported object is Product2. | Required | 63.0 |
| `mainRecord​Field​Values` | Map<String, String> | Mapping of the API name of the field to its value. The values passed through this map are set for the created record. You can pass the Name field only through this map. | Optional | 63.0 |
| `mainRecord​Id` | String | ID of the record. | Required | 63.0 |

**Response Body for POST:** [Deep Clone Response](./connect_responses_deep_clone_response.htm.md "Output representation of the details of the cloned record.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_deep_clone.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
