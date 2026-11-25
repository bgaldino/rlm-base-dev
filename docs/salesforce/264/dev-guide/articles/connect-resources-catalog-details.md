---
page_id: connect-resources-catalog-details
title: Catalog Details (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-catalog-details.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-api-resources
legacy_page_id: connect_resources_catalog_details.htm
fetched_at: 2026-11-25
---

# Catalog Details (POST)

Get catalog details for a specified catalog ID. This API is a composite API for Product Discovery.

## Resource

```
/connect/cpq/catalogs/{catalogId}
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/cpq/catalogs/{0ZSxx000000009hGAA}
```

## Available Version

60.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
  "correlationId": "9cbb9650-48c5-11ed-96d1-0afcf185843b",
  "userContext": {
     "accountId": "001xx0000000001AAA",
     "contactId": "003xx00000000D7AAI"
  }
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `correlation​Id` | String | Unique identifier value that’s attached to the requests and messages, and accepts references to a particular transaction or event chain. | Optional | 60.0 |
| `user​Context` | [User Context Input](./connect-requests-user-context-input.md) | User context details. For example, account ID or contact ID. | Optional | 60.0 |

## Response Body for POST

[CPQ Base Details](./connect-responses-cpq-base-details-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-catalog-details.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
