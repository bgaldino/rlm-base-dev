---
page_id: connect_resources_load_configurator_instance.htm
title: Configuration Load Instance (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_load_configurator_instance.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_resources.htm
fetched_at: 2026-11-23
---

# Configuration Load Instance (POST)

Create a session for the product configuration instance using the transaction ID. Get the session ID that includes the results of actions, such as configuration rules, qualification rules, and pricing management.

## Resource

```
/connect/cpq/configurator/actions/load-instance
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/configurator/actions/load-instance
```

## Available Version

60.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
    "configuratorOptions": 
      {
        "addDefaultConfiguration": true,
        "executeConfigurationRules": true,
        "executePricing": true,
        "qualifyAllProductsInTransaction": true,
        "validateAmendRenewCancel": true,
        "validateProductCatalog": true
    },
    "qualificationContext": {
        "accountId": "001DU000001nHUGYA2"
    },
    "transactionId": "0Q0DU0000000XoN0AU"
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `configurator​Options` | [Configurator Options Input](./connect_requests_configurator_options_input.htm.md "Input representation of the request to get the product configuration options that’s passed to the configurator.") | List of the configurator options to execute. | Optional | 60.0 |
| `context​Mapping​Id` | String | ID of the context mapping record. | Optional | 60.0 |
| `qualification​Context` | [User Context Input](./connect_requests_configurator_user_context_input.htm.md "Input representation of the request to get the context details of a user, which are used for qualification rules.") | Context details that are used for the qualification rules. | Optional | 60.0 |
| `transaction​Id` | String | Transaction ID of the header entity that’s used to create a session. For example, a Quote or an Order. | Required | 60.0 |

## Response Body for POST

[Configuration Load Instance](./connect_responses_load_configuration_instance_output.htm.md "Output representation of the details of the context or session that are returned with a load configuration request.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_load_configurator_instance.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
