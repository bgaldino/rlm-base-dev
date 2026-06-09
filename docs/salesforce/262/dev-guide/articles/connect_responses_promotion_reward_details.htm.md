---
page_id: connect_responses_promotion_reward_details.htm
title: Promotion Reward Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_promotion_reward_details.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Promotion Reward Details

Output representation of the details of the rewards of an eligible promotion
rule.

JSON example
:   ```
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
| `rewardType` | String | Reward type of the promotion. Valid values are:   - `AssignBadge` - `AssignGame` - `CreditFixedPoints` - `CreditMultiplierPoints` - `GiveFreeProduct` - `IssueVoucher` - `ProvideDiscount` | Big, 66.0 | 66.0 |
