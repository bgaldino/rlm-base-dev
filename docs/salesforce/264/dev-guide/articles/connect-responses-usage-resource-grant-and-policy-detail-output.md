---
page_id: connect-responses-usage-resource-grant-and-policy-detail-output
title: Usage Resource Grant And Policy Detail
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-usage-resource-grant-and-policy-detail-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_usage_resource_grant_and_policy_detail_output.htm
fetched_at: 2026-11-25
---

# Usage Resource Grant And Policy Detail

Output representation of the details of a usage resource grant and policy.

## JSON Example

```
{
  "usageResourceGrantAndPolicyDetail": {
    "grantDetail": {
      "grantType": "Grant",
      "id": "1BXxx0000004C9lGAE",
      "quantity": 100,
      "usageGrantNegotiable": "Negotiable",
      "usageRefreshPolicy": {
        "id": "1BYxx0000004C92GAE",
        "negotiable": "Non-Negotiable"
      },
      "usageRolloverPolicy": {
        "id": "1BVxx0000004C93GAE",
        "negotiable": "Non-Negotiable"
      },
      "validityPeriodTerm": 1,
      "validityPeriodUnit": "Month"
    },
    "negotiatedGrantDetail": {
      "grantType": "Grant",
      "id": "1X6xx00000000OECAY",
      "quantity": 100,
      "usageGrantNegotiable": "Negotiable",
      "usageRefreshPolicy": {
        "id": "1BYxx0000004C92GAE",
        "negotiable": "Non-Negotiable"
      },
      "usageRolloverPolicy": {
        "id": "1BVxx0000004C93GAE",
        "negotiable": "Non-Negotiable"
      },
      "validityPeriodTerm": 1,
      "validityPeriodUnit": "Month"
    },
    "negotiatedResourcePolicyDetail": {
      "id": "1X5xx00000000OECAY",
      "ratingFrequencyPolicy": {
        "id": null,
        "negotiable": null
      },
      "usageAggregationPolicy": {
        "id": null,
        "negotiable": null
      },
      "usageCommitmentPolicy": {
        "id": "7Pexx0000004C92CAE",
        "negotiable": "Non-Negotiable"
      },
      "usageOveragePolicy": {
        "id": null,
        "negotiable": null
      }
    },
    "resourcePolicyDetail": {
      "id": "7Suxx0000004C9kCAE",
      "ratingFrequencyPolicy": {
        "id": null,
        "negotiable": null
      },
      "usageAggregationPolicy": {
        "id": null,
        "negotiable": null
      },
      "usageCommitmentPolicy": {
        "id": "7Pexx0000004C92CAE",
        "negotiable": "Non-Negotiable"
      },
      "usageOveragePolicy": {
        "id": null,
        "negotiable": null
      }
    }
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `grant​Detail` | [Grant Detail](./connect-responses-negotiated-grant-detail-output.md) | Details about the grants from the ProductUsageGrant object. | Big, 65.0 | 65.0 |
| `negotiated​Grant​Detail` | [Grant Detail](./connect-responses-negotiated-grant-detail-output.md) | Details about the negotiated grants from the LineItemUsageResourceGrant or TransactionUsageEntitlement object. | Big, 65.0 | 65.0 |
| `negotiated​Resource​PolicyDetail` | [Resource Policy Detail](./connect-responses-resource-policy-detail-output.md) | Details about the policy from the LineItemUsageResourcePolicy or BindingObjectUsageResourcePolicy object. | Big, 65.0 | 65.0 |
| `resourcePolicy​Detail` | [Resource Policy Detail](./connect-responses-resource-policy-detail-output.md) | Details about the policy from the ProductUsageResourcePolicy object. | Big, 65.0 | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-usage-resource-grant-and-policy-detail-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
