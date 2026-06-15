---
page_id: connect_responses_product_recommendation_rules_output.htm
title: Product Recommendation Rules
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_recommendation_rules_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: connect_responses_config_rule_output.htm
fetched_at: 2026-06-09
---

# Product Recommendation Rules

Output representation of the details of the product recommendation rules.

JSON example
:   ```
    {
      "productRecommendationRules": [
        {
          "message": "32GB RDIMM recommends 16GB RDIMM",
          "productIds": [
            "01tVW000003l7uaYAA"
          ],
          "recordType": "Type",
          "referenceId": "0Q0VW000000z8yN0AQ"
        },
        {
          "message": "32GB RDIMM recommends 64GB RDIMM",
          "productIds": [
            "01tVW000003l7v6YAA"
          ],
          "recordType": "Type",
          "referenceId": "0Q0VW000000z8yN0AQ"
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `message` | String | Message to display with the product recommendation. | Small, 67.0 | 67.0 |
| `productIds` | String[] | List of recommended Product IDs. | Small, 67.0 | 67.0 |
| `recordType` | String | Record type associated with the recommendation. | Small, 67.0 | 67.0 |
| `referenceId` | String | Reference ID of the product recommendation rule. | Small, 67.0 | 67.0 |
