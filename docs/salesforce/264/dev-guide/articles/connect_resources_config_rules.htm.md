---
page_id: connect_resources_config_rules.htm
title: Config Rules (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_config_rules.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_resources.htm
fetched_at: 2026-11-23
---

# Config Rules (POST)

Run rules for a specific quote or order based on a context ID or transaction ID.

## Resource

```
/revenue/product-configurator/rules/actions/execute
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v67.0/revenue/product-configurator/rules/actions/execute
```

## Available Version

67.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
  "transactionContextId": "008d27d7-e004-4906-a949-ee7d7c323c77",
  "transactionId": "0Q0DU0000005tJh0AI",
  "ruleOptions": {
    "isUpdateContextRequired": false
  }
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `ruleOptions` | [Config Rule Options Input](./connect_requests_config_rule_options_input.htm.md "Input representation of the details of the configuration rule options.")[] | Details of the options to run specific steps in rules. | Optional | 67.0 |
| `transactionContextId` | String | ID of the sales transaction context instance. | Required if the `transactionId` property isn’t specified. | 67.0 |
| `transactionId` | String | ID of the quote or order. | Required if the `transactionContextId` property isn’t specified. | 67.0 |

## Response Body for POST

[Configuration Rule Response](./connect_responses_config_rule_output.htm.md "Output representation of the details of the configuration rule response.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_config_rules.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
