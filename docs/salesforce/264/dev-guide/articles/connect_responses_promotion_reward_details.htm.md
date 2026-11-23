---
page_id: connect_responses_promotion_reward_details.htm
title: Promotion Reward Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_promotion_reward_details.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-11-23
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

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_promotion_reward_details.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
