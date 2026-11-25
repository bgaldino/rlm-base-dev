---
page_id: connect-resources-set-product-quantity
title: Product Set Quantity (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-set-product-quantity.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: product-configurator-business-apis-resources
legacy_page_id: connect_resources_set_product_quantity.htm
fetched_at: 2026-11-25
---

# Product Set Quantity (POST)

Set the quantity of a product through the runtime system.

## Resource

```
/connect/cpq/configurator/actions/set-product-quantity
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/cpq/configurator/actions/set-product-quantity
```

## Available Version

60.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
    "configuratorOptions": {
        "executePricing": true,
        "returnProductCatalogData": true,
        "qualifyAllProductsInTransaction": true,
        "validateProductCatalog": true,
        "validateAmendRenewCancel": true,
        "executeConfigurationRules": true,
        "addDefaultConfiguration": true
    },
    "qualificationContext": {
        "accountId": "001xx0000000001AAA",
        "contactId": "003xx00000000D7AAI"
    },
    "contextId": "008d27d7-e004-4906-a949-ee7d7c323c77",
    "quantity": 20,
    "transactionLinePath": "Quote.QuoteLineItem.Quantity"
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `configurator​Options` | [Configurator Options Input](./connect-requests-configurator-options-input.md) | List of the configuration options to execute. | Optional | 60.0 |
| `context​Id` | String | ID of the context object that’s being considered. | Required | 60.0 |
| `qualification​Context` | [User Context Input](./connect-requests-configurator-user-context-input.md) | Context details that are used for the qualification rules. | Optional | 60.0 |
| `quantity` | Integer | Value of the product quantity. | Required | 60.0 |
| `transaction​Line​Path` | String[] | Path to the line item where the update to the quantity is applied. For example, Quote.QuoteLineItem.Quantity. | Required | 60.0 |

## Response Body for POST

[Product Quantity Set Configurator](./connect-responses-set-product-quantity-configurator-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-set-product-quantity.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
