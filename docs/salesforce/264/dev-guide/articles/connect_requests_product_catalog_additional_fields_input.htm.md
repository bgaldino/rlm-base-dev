---
page_id: connect_requests_product_catalog_additional_fields_input.htm
title: Additional Fields Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_product_catalog_additional_fields_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-11-23
---

# Additional Fields Input

Input representation of the additional standard or custom fields to be included in the response.

**JSON Example**

```
"additionalFields": {
    "Product2": {
      "fields": [
        "code__c"
      ]
    }
```

This example shows a sample request with attribute definition field details.

```
"additionalFields":{
  "OptOutAssetization":true
  "OptOutDecompositionAction":false
  "OptOutSupplementalAction":false
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `fields` | String[] | List of additional standard or custom fields to be included in the response. | Required | 61.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_product_catalog_additional_fields_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
