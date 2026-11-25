---
page_id: connect-resources-save-configuration-instance
title: Configuration Save Instance (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-save-configuration-instance.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: product-configurator-business-apis-resources
legacy_page_id: connect_resources_save_configuration_instance.htm
fetched_at: 2026-11-25
---

# Configuration Save Instance (POST)

Save a configuration instance after a successful product configuration.

Use the Configuration Save Instance API to save the changes to the source after a successful configuration. For example, save changes to the quote line item of a product, which is the source used to load the configuration.

## Resource

```
/connect/cpq/configurator/actions/save-instance
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/cpq/configurator/actions/save-instance
```

## Available Version

60.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
"contextId": "008d27d7-e004-4906-a949-ee7d7c323c77"
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextId` | String | Transaction context ID of the product configuration instance that’s to be saved. | Required | 60.0 |

## Response Body for POST

[Configuration Save Instance](./connect-responses-save-configuration-instance-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-save-configuration-instance.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
