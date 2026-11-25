---
page_id: connect-responses-promotion-reward-details
title: Promotion Reward Details
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-promotion-reward-details.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-responses
legacy_page_id: connect_responses_promotion_reward_details.htm
fetched_at: 2026-11-25
---

# Promotion Reward Details

Output representation of the details of the rewards of an eligible promotion rule.

## JSON Example

```
{
  "ruleRewards": [
    {
      "rewardDetails": {
        "discountLevel": "Line",
        "discountProduct": "Printer Paper",
        "discountType": "AmountOff",
        "discountValue": "2.0",
        "discountAppliedAt": "LineItem"
      },
      "rewardType": "ProvideDiscount"
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `rewardDetails` | Map<String, Object> | Details of the reward offered by the promotion rule. | Big, 66.0 | 66.0 |
| `rewardType` | String | Reward type of the promotion. Valid values are `AssignBadge`, `AssignGame`, `CreditFixedPoints`, `CreditMultiplierPoints`, `GiveFreeProduct`, `IssueVoucher`, or `ProvideDiscount`. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-promotion-reward-details.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
