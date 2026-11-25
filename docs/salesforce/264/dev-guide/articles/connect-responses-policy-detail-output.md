---
page_id: connect-responses-policy-detail-output
title: Policy Details
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-policy-detail-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_policy_detail_output.htm
fetched_at: 2026-11-25
---

# Policy Details

Output representation of the details of a policy.

## JSON Example

This example includes the details for different policy types.

```
{
  "bindingObjectGrantDetail": [
    {
      "effectiveEndDate": "Sat Oct 04 23:59:59 GMT 2025",
      "effectiveStartDate": "Fri Sep 05 00:00:00 GMT 2025",
      "grantType": "Grant",
      "id": "1B0SB0000000Eiv0AE",
      "product": {
        "id": "01tSB000006XMtqYAG"
      },
      "quantity": 100,
      "record": {
        "id": "02iSB000000IoETYA0"
      },
      "unitOfMeasure": {
        "id": "0hESB0000003yfp2AA"
      },
      "usageRefreshPolicy": {
        "id": "1BYSB0000001lOH4AY",
        "negotiable": null
      },
      "usageRolloverPolicy": {
        "id": "1BVSB000000A1xJ4AS",
        "negotiable": null
      },
      "validityPeriodTerm": 1,
      "validityPeriodUnit": "Month"
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the policy. | Big, 65.0 | 65.0 |
| `negotiable` | String | Indicates whether the policy is negotiable. Valid values are `Negotiable` or `Non-Negotiable`. | Big, 65.0 | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-policy-detail-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
