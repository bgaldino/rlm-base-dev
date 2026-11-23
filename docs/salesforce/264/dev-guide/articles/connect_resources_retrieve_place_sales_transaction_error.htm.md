---
page_id: connect_resources_retrieve_place_sales_transaction_error.htm
title: Retrieve Sales Transaction API Errors (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_retrieve_place_sales_transaction_error.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_business_apis_rest_references.htm
fetched_at: 2026-11-23
---

# Retrieve Sales Transaction API Errors (GET)

Retrieve any asynchronous error details associated with a sales transaction request.

This API returns detailed error status and a retryable payload from [Place Sales Transaction API](./connect_resources_place_sales_transaction.htm.md "HTML (New Window)") that runs asynchronously. Also, view any blocking errors that prevent a subrequest from persisting. This request doesn’t return any non-blocking warnings, such as configuration or tax warnings.

You can view the list of `rollbackedReferenceIds`, which shows synthetic or reference IDs that roll back when the batch fails.

## Resource

```
connect/revenue/transaction-management/sales-transactions/actions/place/trackerId/errors
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/revenue/transaction-management/sales-transactions/actions/place/16PRM0000004DBq/errors
```

## Available Version

66.0

## HTTP Methods

GET

## Request Parameter for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `includeRetryable​Payload` | Boolean | Indicates whether to return a subset of the original Place Sales Transaction API payload errors (`true`) or not (`false`). The default value is `false`. | Optional | 66.0 |

## Response Body for GET

[Sales Transaction Async Error](./connect_responses_place_sales_transaction_async_error_output.htm.md "Output representation of the details of errors encountered during the async processing of the Place Sales Transaction API request.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_retrieve_place_sales_transaction_error.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
