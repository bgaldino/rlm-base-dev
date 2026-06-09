---
page_id: connect_responses_visibility_rules_output.htm
title: Visibility Rules
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_visibility_rules_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: connect_responses_config_rule_output.htm
fetched_at: 2026-06-09
---

# Visibility Rules

Output representation of the details of the visibility rules.

JSON example
:   ```
    {
      "visibilityRules": [
        {
          "message": "128GB LRDIMM disables 16GB RDIMM",
          "productIds": [
            "01tVW000003l7uaYAA"
          ],
          "scope": "virtual",
          "target": "product",
          "type": "disable"
        },
        {
          "message": "Additional API disables Additional API Gov",
          "productIds": [
            "01tVW000003l7tzYAA"
          ],
          "scope": "virtual",
          "target": "product",
          "type": "disable"
        },
        {
          "message": "Disable All other API Products",
          "productIds": [
            "01tVW000003l7u0YAA",
            "01tVW000003l7u1YAA"
          ],
          "scope": "virtual",
          "target": "product",
          "type": "disable"
        },
        {
          "message": "32GB RDIMM disables 128GB LRDIMM",
          "productIds": [
            "01tVW000003l7v5YAA"
          ],
          "scope": "virtual",
          "target": "product",
          "type": "disable"
        },
        {
          "message": "API Access Requests AEH disables Additional API Prod",
          "productIds": [
            "01tVW000003l7u1YAA"
          ],
          "scope": "virtual",
          "target": "product",
          "type": "disable"
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `attributeId` | String | ID of the attribute associated with this visibility rule. | Small, 67.0 | 67.0 |
| `attribute​Picklist​ValueId` | String | ID of the attribute picklist value associated with this visibility rule. | Small, 67.0 | 67.0 |
| `message` | String | Message to display when the visibility rule is applied. | Small, 67.0 | 67.0 |
| `prcId` | String | ID of the Product Relationship Configuration (PRC) associated with this visibility rule. | Small, 67.0 | 67.0 |
| `productIds` | String[] | List of product IDs affected by this visibility rule. | Small, 67.0 | 67.0 |
| `scope` | String | Scope of the visibility rule. Valid values are:   - `PRODUCT` - `BUNDLE` - `VIRTUAL` | Small, 67.0 | 67.0 |
| `stiId` | String | ID of the sales transaction item associated with this visibility rule. | Small, 67.0 | 67.0 |
| `target` | String | Target of the visibility rule. Valid values are:   - `COMPONENT` - `QUANTITY` - `ATTRIBUTE` - `ATTRIBUTE_PICKLIST_VALUE` - `PRODUCT` | Small, 67.0 | 67.0 |
| `type` | String | Type of visibility rule. Valid values are:   - `HIDE` - `DISABLE` | Small, 67.0 | 67.0 |
