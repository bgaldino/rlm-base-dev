---
page_id: connect_requests_usage_product_validation_input.htm
title: Usage Product Validation Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_usage_product_validation_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_requests.htm
fetched_at: 2026-11-23
---

# Usage Product Validation Input

Input representation of the usage product validation request.

## JSON Example

```
{
  "productIds": [
    "01txx0000006i2gAAA",
    "01txx0000006j2gAAA"
  ],
  "startDate": "2024-01-01T00:00:00Z",
  "endDate": "2024-12-31T23:59:59Z"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `productIds` | String[] | List of product IDs to be validated. The maximum limit is `10` valid product IDs. | Required | 66.0 |
| `startDate` | String | Start date of the date range in which all active records are validated. | Optional | 66.0 |
| `endDate` | String | End date of the date range in which all active records are validated. | Optional | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_usage_product_validation_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
