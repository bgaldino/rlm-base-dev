---
page_id: connect-requests-configurator-deleted-node-input
title: Configurator Deleted Node Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-configurator-deleted-node-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: product-configurator-business-apis-requests
legacy_page_id: connect_requests_configurator_deleted_node_input.htm
fetched_at: 2026-11-25
---

# Configurator Deleted Node Input

Input representation of the nodes to be deleted from a product configuration.

## JSON Example

```
    "deletedNodes": [
        {
            "path": ["0Q0DE000000ISHJs81", "0QLDE000000IBXw4AO"]
        }
    ]
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `path` | String[] | Path to the node that’s being deleted. | Required | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-configurator-deleted-node-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
