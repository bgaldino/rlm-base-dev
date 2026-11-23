---
page_id: connect_requests_context_info_input.htm
title: Context Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_context_info_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-11-23
---

# Context Input

Input representation of the context that's associated with a sales transaction for a quote or an order.

## JSON Example

```
{
  "contextDetails": {
    "contextId": "e055bb18-d4e8-41c3-881e-0132b9561708"
  }
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextId` | String | ID of the context that represents the created session for the sales transaction. This property is supported only for a PATCH request. If the `contextId` property isn’t specified, the Place Sales Transaction API generates the context ID for the sales transaction. | Optional | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_context_info_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
