---
page_id: connect-requests-configurator-preference-input
title: Configurator Preference Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-configurator-preference-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-requests
legacy_page_id: connect_requests_configurator_preference_input.htm
fetched_at: 2026-11-25
---

# Configurator Preference Input

Input representation of the configuration preference for the place sales transaction request.

## JSON Example

```
{
  "configurationPref": {
    "configurationMethod": "Skip",
    "configurationOptions": {
      "validateProductCatalog": true,
      "validateAmendRenewCancel": true,
      "executeConfigurationRules": true,
      "addDefaultConfiguration": true
    }
  }
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `configuration​Method` | String | Configuration method for the place sales transaction request. Valid values are `Force`—Specifies to enforce the predefined configuration process during the sales transaction process, `Skip`—Specifies to skip the configuration process during the quote creation process, or `System`—Specifies the system to determine whether the configuration process is required. The default value is `Skip`. | Optional | 63.0 |
| `configuration​Options` | [Configuration Options Input](./connect-requests-configuration-options-input.md) | Configuration options during the ingestion process. | Optional | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-configurator-preference-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
