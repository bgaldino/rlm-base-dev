---
page_id: connect-responses-negotiated-grant-detail-output
title: Grant Detail
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-negotiated-grant-detail-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_negotiated_grant_detail_output.htm
fetched_at: 2026-11-25
---

# Grant Detail

Output representation of the details of a grant from the ProductUsageGrant, LineItemUsageResourceGrant, or TransactionUsageEntitlement objects.

## JSON Example

```
{
  "negotiatedGrantDetail": {
    "grantType": "Grant",
    "id": "1X6xx00000000OECAY",
    "quantity": 100,
    "usageGrantNegotiable": "Negotiable",
    "usageRefreshPolicy": {
      "displayName": null,
      "id": "1BYxx0000004C92GAE",
      "negotiable": "Non-Negotiable"
    },
    "usageRolloverPolicy": {
      "displayName": null,
      "id": "1BVxx0000004C92GAE",
      "negotiable": "Non-Negotiable"
    },
    "validityPeriodTerm": 12,
    "validityPeriodUnit": "Month"
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `grantType` | String | Details about the grant type. | Big, 65.0 | 65.0 |
| `id` | String | ID of the usage resource grant. | Big, 65.0 | 65.0 |
| `quantity` | Double | Quantity of the negotiated usage resource grant. | Big, 65.0 | 65.0 |
| `usageGrant​Negotiable` | String | Specifies whether the grant is negotiable or not. | Big, 65.0 | 65.0 |
| `usageRefresh​Policy` | [Policy Detail](./connect-responses-policy-detail-output.md) | ID of the usage grant refresh policy. | Big, 65.0 | 65.0 |
| `usageRollover​Policy` | [Policy Detail](./connect-responses-policy-detail-output.md) | ID of the usage grant rollover policy. | Big, 65.0 | 65.0 |
| `validity​PeriodTerm` | Double | Validity period term of the grant. | Big, 65.0 | 65.0 |
| `validity​PeriodUnit` | String | Validity period unit of the grant. | Big, 65.0 | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-negotiated-grant-detail-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
