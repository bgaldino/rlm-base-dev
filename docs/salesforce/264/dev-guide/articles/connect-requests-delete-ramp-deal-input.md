---
page_id: connect-requests-delete-ramp-deal-input
title: Delete Ramp Deal Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-delete-ramp-deal-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-requests
legacy_page_id: connect_requests_delete_ramp_deal_input.htm
fetched_at: 2026-11-25
---

# Delete Ramp Deal Input

Input representation of the request to delete a ramp deal.

## JSON Example

```
{
  "rampDealIds": [
    "0Q0xx0000004CDxCAM",
    "0QLxx0000004CSOGA2"
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `rampDeal​Ids` | String[] | Ramp identifier on the quote line item or order item. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-delete-ramp-deal-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
