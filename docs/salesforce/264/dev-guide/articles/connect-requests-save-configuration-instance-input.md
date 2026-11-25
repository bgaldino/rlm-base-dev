---
page_id: connect-requests-save-configuration-instance-input
title: Configuration Save Instance Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-save-configuration-instance-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: product-configurator-business-apis-requests
legacy_page_id: connect_requests_save_configuration_instance_input.htm
fetched_at: 2026-11-25
---

# Configuration Save Instance Input

Input representation of the request to save a product configuration instance.

## JSON Example

```
{
"contextId": "008d27d7-e004-4906-a949-ee7d7c323c77"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextId` | String | Transaction context ID of the product configuration instance that’s to be saved. | Required | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-save-configuration-instance-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
