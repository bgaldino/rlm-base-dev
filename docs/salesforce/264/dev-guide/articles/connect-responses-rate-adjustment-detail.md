---
page_id: connect-responses-rate-adjustment-detail
title: Adjustment Details
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-rate-adjustment-detail.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Rate Management
parent_page: rate-management-business-apis-responses
legacy_page_id: connect_responses_rate_adjustment_detail.htm
fetched_at: 2026-11-25
---

# Adjustment Details

Output representation of a rate adjustment request.

## JSON Example

```
 "pricingElement": {
      "adjustments": [{
      "adjustmentType": null,
      "adjustmentValue": null
    }],
      "name": "List Price",
      "elementType": "ListPrice"
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `adjustments` | Map<String, Object>[] | Details of the rate element. | Small, 60.0 | 60.0 |
| `description` | String | Description of the rate element. | Small, 60.0 | 60.0 |
| `element​Type` | String | Type of the rate element. | Small, 60.0 | 60.0 |
| `name` | String | Name of the rate element. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-rate-adjustment-detail.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
