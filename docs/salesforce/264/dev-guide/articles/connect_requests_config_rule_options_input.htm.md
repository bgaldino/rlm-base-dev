---
page_id: connect_requests_config_rule_options_input.htm
title: Configuration Rule Options Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_config_rule_options_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: connect_requests_config_rule_input.htm
fetched_at: 2026-11-23
---

# Configuration Rule Options Input

Input representation of the details of the configuration rule options.

## JSON Example

```
{
  "ruleOptions": {
    "isUpdateContextRequired": false
  }
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `isUpdateContextRequired` | Boolean | Indicates whether context update is required with the capability to automatically add or delete a product and its components (`true`) or not (`false`). If Place Sales Transaction API is invoked with configuration enabled, set this property to `false` to avoid any redundant execution of context logic. | Optional | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_config_rule_options_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
