---
page_id: connect-responses-binding-object-resource-policy-detail-output
title: Binding Object Resource Policy Detail
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-binding-object-resource-policy-detail-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_binding_object_resource_policy_detail_output.htm
fetched_at: 2026-11-25
---

# Binding Object Resource Policy Detail

Output representation of the details of a usage resource policy.

## JSON Example

This example includes the details of a usage resource policy.

```
{
  "bindingObjectResourcePolicyDetail": {
    "drawdownOrder": "ExpiringFirst",
    "id": "1X2SB00000002WT0AY",
    "ratingFrequencyPolicy": {
      "id": "1HJSB0000000G3B4AU",
      "negotiable": null
    },
    "usageAggregationPolicy": {
      "id": "1cfSB0000001xHPYAY",
      "negotiable": null
    },
    "usageCommitmentPolicy": {
      "id": null,
      "negotiable": null
    },
    "usageOveragePolicy": {
      "id": "7UkSB00000002OP0AY",
      "negotiable": null
    }
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `drawdown​Order` | String | Specifies the order or way to process the drawdown. See [Usage Management Essentials](https://help.salesforce.com/s/articleView?id=ind.usage_management_essentials.htm) to know more about a drawdown process. | Big, 65.0 | 65.0 |
| `id` | String | ID of the `Binding Object Usage Resource Policy` record. | Big, 65.0 | 65.0 |
| `ratingFrequency​Policy` | [Policy Detail](./connect-responses-policy-detail-output.md) | Details of the rating frequency policy. | Big, 65.0 | 65.0 |
| `usageAggregation​Policy` | [Policy Detail](./connect-responses-policy-detail-output.md) | Details of the usage aggregation policy. | Big, 65.0 | 65.0 |
| `usageCommitment​Policy` | [Policy Detail](./connect-responses-policy-detail-output.md) | Details of the commitment policy of the usage resource. | Big, 65.0 | 65.0 |
| `usageOverage​Policy` | [Policy Detail](./connect-responses-policy-detail-output.md) | Details of the overage policy of the usage resource. | Big, 65.0 | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-binding-object-resource-policy-detail-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
