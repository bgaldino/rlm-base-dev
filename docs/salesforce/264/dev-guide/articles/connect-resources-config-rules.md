---
page_id: connect-resources-config-rules
title: Config Rules (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-config-rules.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: product-configurator-business-apis-resources
legacy_page_id: connect_resources_config_rules.htm
fetched_at: 2026-11-25
---

# Config Rules (POST)

Run rules for a specific quote or order based on a context ID or transaction ID.

## Resource

```
/revenue/product-configurator/rules/actions/execute
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v67.0/revenue/product-configurator/rules/actions/execute
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
| `ruleOptions` | [Config Rule Options Input](./connect-requests-config-rule-options-input.md)[] | Details of the options to run specific steps in rules. | Optional | 67.0 |
| `transactionContextId` | String | ID of the sales transaction context instance. | Required if the `transactionId` property isn’t specified. | 67.0 |
| `transactionId` | String | ID of the quote or order. | Required if the `transactionContextId` property isn’t specified. | 67.0 |

## Response Body for POST

[Configuration Rule Response](./connect-responses-config-rule-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-config-rules.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
