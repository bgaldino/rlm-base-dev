---
page_id: connect_responses_catalogs_output.htm
title: Catalogs Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_catalogs_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-11-23
---

# Catalogs Output

Output representation of the retrieved catalog result.

## JSON Example

```
{
  "catalogs": [
    {
      "catalogType": "Sales",
      "code": "CAT009",
      "id": "0ZS1Q000000XbZAWA0",
      "name": "SmartBytes B2B Catalog",
      "numberOfCategories": 8
    }
  ],
  "correlationId": "0b7b6a30-895c-407a-91b3-e67482d339a3",
  "count": 1,
  "status": {
    "code": "200",
    "errors": [],
    "message": "Successfully fetched the catalog records."
  }
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `catalogs` | [Catalog Output](./connect_responses_catalog_output.htm.md "Output representation of the catalog definition.")[] | List of the catalogs. | Small, 60.0 | 60.0 |
| `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Small, 60.0 | 60.0 |
| `count` | Integer | Total number of the catalog records retrieved after the query execution, wherein the `pageSize` property determines the number of records returned in every page. | Small, 60.0 | 60.0 |
| `status` | [Status](./connect_responses_status.htm.md "Output representation of the status of the request.") | Status of the request. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_catalogs_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
