---
page_id: connect_responses_product_configuration_rules_output.htm
title: Product Configuration Rules
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_configuration_rules_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_responses.htm
fetched_at: 2026-06-09
---

# Product Configuration Rules

Output representation of the details of the product configuration rules.

JSON example
:   ```
    {
      "configurationRules": [
        {
          "details": [
            {
              "message": "recommend Mouse from monitor"
            }
          ],
          "type": "recommend"
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `details` | [Product Configuration Rule Details](./connect_responses_product_configuration_rule_details_output.htm.md "Output representation of the product configuration rule details.")[] | Details of the product configuration rule. | Small, 67.0 | 67.0 |
| `type` | String | Type of the product configuration rule. | Small, 67.0 | 67.0 |
