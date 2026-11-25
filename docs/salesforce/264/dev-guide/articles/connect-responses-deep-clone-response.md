---
page_id: connect-responses-deep-clone-response
title: Deep Clone Response
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-deep-clone-response.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_deep_clone_response.htm
fetched_at: 2026-11-25
---

# Deep Clone Response

Output representation of the details of the cloned record.

## JSON Example

```
{
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
  ],
  "createdRootRecordId": "01tSG0000030Yb3YAE",
  "errorList": [],
  "isSuccessful": true
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `created​RecordList` | [Deep Clone Record Response](./connect-responses-deep-clone-record-response.md)[] | List of cloned related records of the main record. | Small, 63.0 | 63.0 |
| `createdRoot​RecordId` | String | ID of the created root record. | Small, 63.0 | 63.0 |
| `error​List` | [Deep Clone Error](./connect-responses-deep-clone-error.md)[] | Details of errors, if any. | Small, 63.0 | 63.0 |
| `error​Message` | String | Error message if the API request fails. | Small, 63.0 | 63.0 |
| `is​Successful` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-deep-clone-response.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
