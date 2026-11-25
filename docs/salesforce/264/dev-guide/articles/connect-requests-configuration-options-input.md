---
page_id: connect-requests-configuration-options-input
title: Configuration Options Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-configuration-options-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-requests
legacy_page_id: connect_requests_configuration_options_input.htm
fetched_at: 2026-11-25
---

# Configuration Options Input

Input representation for the configuration options.

## JSON Example

```
{
  "configurationOptions": {
    "validateProductCatalog": true,
    "validateAmendRenewCancel": true,
    "executeConfigurationRules": true,
    "addDefaultConfiguration": true
  }
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `addDefault​Configuration` | Boolean | Indicates whether to automatically add default configurations to the order (`true`) or not (`false`). | Optional | 60.0 |
| `execute​Configuration​Rules` | Boolean | Indicates whether the order must adhere to configuration rules during processing (`true`) or bypass them (`false`). | Optional | 60.0 |
| `validate​Amend​Renew​Cancel` | Boolean | Indicates whether to run validations related to amend, renew, or cancel processes (`true`) or not (`false`). | Optional | 60.0 |
| `validate​Product​Catalog` | Boolean | Indicates whether the order must be validated against the product catalog (`true`) or not (`false`). | Optional | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-configuration-options-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
