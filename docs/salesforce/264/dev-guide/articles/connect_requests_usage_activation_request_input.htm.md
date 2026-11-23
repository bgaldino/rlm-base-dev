---
page_id: connect_requests_usage_activation_request_input.htm
title: Usage Activation Request Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_usage_activation_request_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_requests.htm
fetched_at: 2026-11-23
---

# Usage Activation Request Input

Input representation for a single product entry in a usage product activation request. Each entry identifies one product and the usage resources to activate for that product.

## JSON Example

```
{
  "productId": "01txx0000006i2gAAA",
  "usageResourceIds": [
    "0hUxx000000001",
    "0hUxx000000002"
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `product​Id` | String | ID of the Product2 record whose associated usage records are activated. | Required | 67.0 |
| `usage​Resource​Ids` | String[] | List of usage resource IDs to activate for the given product. The activation extends to all design-time records linked to these resources, such as product usage grants, usage policies, units of measure, units of measure classes, and rate card entries. If this property is empty or omitted, all usage records associated with the given product are activated. | Optional | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_usage_activation_request_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
