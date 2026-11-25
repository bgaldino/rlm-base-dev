---
page_id: connect-responses-unit-of-measure-status
title: Unit of Measure Status
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-unit-of-measure-status.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_unit_of_measure_status.htm
fetched_at: 2026-11-25
---

# Unit of Measure Status

Output representation of the status of the Unit of Measure API request.

## JSON Example

```
  "status": {
    "errors": [],
    "httpStatusCode": "200",
    "message": " Successfully fetched UnitOfMeasure Info. "
  }
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Unit Of Measure Error](./connect-responses-unit-of-measure-error-output.md)[] | Errors encountered during the processing of the API request. | Small, 63.0 | 63.0 |
| `httpStatus​Code` | String | HTTP status code of the API request. | Small, 63.0 | 63.0 |
| `message` | String | Localized response message. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-unit-of-measure-status.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
