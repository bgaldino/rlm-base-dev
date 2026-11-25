---
page_id: connect-resources-cpq-qualification
title: Qualification (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-cpq-qualification.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-api-resources
legacy_page_id: connect_resources_cpq_qualification.htm
fetched_at: 2026-11-25
---

# Qualification (POST)

Run the qualification procedure on a list of product IDs. This API is a composite API for Product Discovery.

## Resource

```
/connect/cpq/qualification
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/cpq/qualification
```

## Available Version

60.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
  "productIds": [
    "01txx0000006i7PAAQ",
    "01txx0000006i7QAAQ",
    "01txx0000006i7IAAQ"
  ],
  "userContext": {
    "accountId": "001xx000003GZHgAAO"
  }
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `additional​ContextData` | [Context Data Input](./connect-requests-context-data-input.md)[] | Additional nodes that are added to the custom or default context definition. The maximum number of supported nodes is 10. | Optional | 60.0 |
| `catalog​Id` | String | ID of the catalog. | Optional | 60.0 |
| `category​Id` | String | ID of the category. | Optional | 60.0 |
| `context​Definition` | String | API name of the custom context definition that’s sent for context creation. If this property isn’t specified, the default context definition is used. | Optional | 60.0 |
| `context​Mapping` | String | Default context mapping of the context definition. If a context mapping is specified, then the API checks whether the mapping belongs to the specified context definition to process the details for hydration. | Optional | 60.0 |
| `correlation​Id` | String | Unique identifier of the request. | Optional | 60.0 |
| `product​Ids` | String[] | List of product IDs for qualification check. | Required | 60.0 |
| `qualification​Procedure` | String | API name of the custom qualification procedure that’s sent for processing. If this property isn’t specified, the default qualification procedure is executed. | Optional | 60.0 |
| `user​Context` | [User Context Input](./connect-requests-user-context-input.md) | User context details. For example, account ID or contact ID. | Optional | 60.0 |

## Response Body for POST

[CPQ Base List](./connect-responses-cpq-base-list-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-cpq-qualification.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
