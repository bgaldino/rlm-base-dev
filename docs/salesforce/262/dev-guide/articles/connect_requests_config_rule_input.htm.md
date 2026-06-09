---
page_id: connect_requests_config_rule_input.htm
title: Configuration Rule Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_config_rule_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Configuration Rule Input

Input representation of the details of a configuration rule.

JSON example
:   ```
    {
      "transactionContextId": "008d27d7-e004-4906-a949-ee7d7c323c77",
      "transactionId": "0Q0DU0000005tJh0AI",
      "ruleOptions": {
        "isUpdateContextRequired": false
      }
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `ruleOptions` | [Config Rule Options Input](./connect_requests_config_rule_options_input.htm.md "Input representation of the details of the configuration rule options.")[] | Details of the options to run specific steps in rules. | Optional | 67.0 |
    | `transactionContextId` | String | ID of the sales transaction context instance. | Required if the `transactionId` property isn’t specified. | 67.0 |
    | `transactionId` | String | ID of the quote or order. | Required if the `transactionContextId` property isn’t specified. | 67.0 |

- **[Configuration Rule Options Input](./connect_requests_config_rule_options_input.htm.md)**  
  Input representation of the details of the configuration rule options.
