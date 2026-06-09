---
page_id: connect_responses_promotion_rules_list.htm
title: Promotion Rules List
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_promotion_rules_list.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Promotion Rules List

Output representation of the details of the rules of an eligible promotion.

JSON example
:   ```
    {
      "promotionEligibleRules": [
        {
          "ruleName": "Rule001",
          "rulePriority": 1,
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
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `ruleName` | String | Rule name in the promotion which is eligible for rewards. | Big, 66.0 | 66.0 |
| `rulePriority` | Integer | Rule priority in the promotion which is eligible for rewards. | Big, 66.0 | 66.0 |
| `ruleRewards` | [Promotion Reward Details](./connect_responses_promotion_reward_details.htm.md "Output representation of the details of the rewards of an eligible promotion rule.")[] | Rewards associated with the eligible rule. | Big, 66.0 | 66.0 |
