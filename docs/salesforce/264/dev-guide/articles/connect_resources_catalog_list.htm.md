---
page_id: connect_resources_catalog_list.htm
title: Catalog List (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_catalog_list.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_resources.htm
fetched_at: 2026-11-23
---

# Catalog List (POST)

Get a paginated list of catalogs. This API is a composite API for Product Discovery.

## Resource

```
/connect/cpq/catalogs
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/catalogs
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
    "limit": 10,
    "offset": 0,
    "orderBy": [
        "name:asc",
        "id:desc"
    ],
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
| `limit` | Integer | Number of items to include in the response. | Optional | 60.0 |
| `offset` | Integer | Offset size from which to get the catalog count. | Optional | 60.0 |
| `order​By` | String[] | Sort order for the catalogs. | Optional | 60.0 |
| `user​Context` | [User Context Input](./connect_requests_user_context_input.htm.md "Input representation of the details with the user context.") | User context details. For example, account ID or contact ID. | Optional | 60.0 |

## Response Body for POST

[CPQ Base List](./connect_responses_cpq_base_list_output.htm.md "Output representation of the list of catalogs, categories, or products based on the request.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_catalog_list.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
