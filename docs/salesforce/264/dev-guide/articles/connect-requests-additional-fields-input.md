---
page_id: connect-requests-additional-fields-input
title: Additional Fields Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-additional-fields-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-api-requests
legacy_page_id: connect_requests_additional_fields_input.htm
fetched_at: 2026-11-25
---

# Additional Fields Input

Input representation of the additional standard or custom fields to include in the response.

## JSON Example

```
  "additionalFields" : {
    "Product2" : {
    "fields" : ["CustomField1__c","StandardField1"]
}
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `fields` | String[] | List of additional standard or custom fields to include in the response. | Optional | 61.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-additional-fields-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
