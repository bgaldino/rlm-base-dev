---
page_id: connect-responses-deep-clone-record-response
title: Deep Clone Record Response
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-deep-clone-record-response.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_deep_clone_record_response.htm
fetched_at: 2026-11-25
---

# Deep Clone Record Response

Output representation of the details of the cloned related records.

## JSON Example

```
  "createdRecordList": [
    {
      "createdRecordId": "01tSG0000030Yb3YAE",
      "entityApiName": "Product2",
      "entityLabel": "Product"
    },
    {
      "createdRecordId": "0iOSG0000002rMn2AI",
      "entityApiName": "ProductSellingModelOption",
      "entityLabel": "Product Selling Model Option"
    },
    {
      "createdRecordId": "0v7SG0000001ktdYAA",
      "entityApiName": "ProductAttributeDefinition",
      "entityLabel": "Product Attribute Definition"
    }
  ]
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `created​RecordId` | String | ID of the created related record. | Small, 63.0 | 63.0 |
| `entity​ApiName` | String | API name of the created object. | Small, 63.0 | 63.0 |
| `entity​Label` | String | Label of the created object. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-deep-clone-record-response.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
