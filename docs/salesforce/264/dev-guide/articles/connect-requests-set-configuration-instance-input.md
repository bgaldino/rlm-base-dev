---
page_id: connect-requests-set-configuration-instance-input
title: Configuration Set Instance Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-set-configuration-instance-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: product-configurator-business-apis-requests
legacy_page_id: connect_requests_set_configuration_instance_input.htm
fetched_at: 2026-11-25
---

# Configuration Set Instance Input

Input representation of the request to set a product configuration instance.

## JSON Example

```
{
  "configuratorOptions": {
    "addDefaultConfiguration": true,
    "executeConfigurationRules": true,
    "executePricing": false,
    "qualifyAllProductsInTransaction": false,
    "validateAmendRenewCancel": false,
    "validateProductCatalog": false
  },
  "contextMappingId": "11jEk000017YdyUIAS",
  "qualificationContext": {
    "accountId": "001DU000001nHUGYA2"
  },
  "transaction": "{\"Quote\":[{\"QuoteLineItem\":[{\"businessObjectType\":\"QuoteLineItem\",\"id\":\"qli_1\"},{\"businessObjectType\":\"QuoteLineItem\",\"id\":\"qli_2\"},{\"businessObjectType\":\"QuoteLineItem\",\"id\":\"qli_3\"},{\"businessObjectType\":\"QuoteLineItem\",\"id\":\"qli_4\"}],\"businessObjectType\":\"Quote\",\"id\":\"aJSdm0000003m3JGAQ\"}]}"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `configurator​Options` | [Configurator Options Input](./connect-requests-configurator-options-input.md) | List of the configurator options to execute. | Optional | 60.0 |
| `context​MappingId` | String | ID of the context mapping record. | Required | 60.0 |
| `qualification​Context` | [User Context Input](./connect-requests-configurator-user-context-input.md) | Context details that are used for the qualification rules. | Optional | 60.0 |
| `transaction` | String | Transaction JSON payload representing an object in an external system that’s used to create a session. | Required | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-set-configuration-instance-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
