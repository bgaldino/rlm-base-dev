---
page_id: connect-resources-delete-nodes
title: Configurator Delete Nodes (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-delete-nodes.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: product-configurator-business-apis-resources
legacy_page_id: connect_resources_delete_nodes.htm
fetched_at: 2026-11-25
---

# Configurator Delete Nodes (POST)

Delete nodes from a product configuration.

## Resource

```
/connect/cpq/configurator/actions/delete-nodes
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/cpq/configurator/actions/delete-nodes
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
    "deletedNodes": [
        {
            "path": ["0Q0DE000000ISHJs81", "0QLDE000000IBXw4AO"]
        }
    ]
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `configurator​Options` | [Configurator Options Input](./connect-requests-configurator-options-input.md) | List of the configuration options to execute. | Optional | 60.0 |
| `context​Id` | String | ID of the context object that’s being considered. | Required | 60.0 |
| `deleted​Nodes` | [Configurator Deleted Node Input](./connect-requests-configurator-deleted-node-input.md)[] | List of the nodes to be deleted. | Required | 60.0 |
| `qualification​Context` | [User Context Input](./connect-requests-configurator-user-context-input.md) | Context details that are used for the qualification rules. | Optional | 60.0 |

## Response Body for POST

[Configurator Delete Nodes](./connect-responses-delete-nodes-configurator-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-delete-nodes.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
