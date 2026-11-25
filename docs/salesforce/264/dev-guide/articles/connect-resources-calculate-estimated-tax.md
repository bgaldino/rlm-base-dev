---
page_id: connect-resources-calculate-estimated-tax
title: Invoice Estimated Tax Calculation (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-calculate-estimated-tax.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_calculate_estimated_tax.htm
fetched_at: 2026-11-25
---

# Invoice Estimated Tax Calculation (POST)

Calculate estimated tax for invoices with invoice lines that have the `TaxProcessingStatus` as either `Pending` or `Estimated`.

## Resource

```
/commerce/invoicing/invoices/collection/actions/calculate-estimated-tax
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/commerce/invoicing/invoices/collection/actions/calculate-estimated-tax
```

## Available Version

63.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
  "invoiceIds": ["3ttxx0000004CIjAAM"]
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `correlationId` | String | Splunk correlation ID to track the messages that are related to the request and are logged in Splunk by the different services involved in the request. If the ID isn’t specified, the service creates a random Universally Unique Identifier (UUID). | Optional | 63.0 |
| `invoiceIds` | String[] | IDs of the invoices for which the estimated tax must be calculated. You can specify one invoice per API request. | Required | 63.0 |

## Response Body for POST

[Revenue Async Response](./connect-responses-revenue-async-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-calculate-estimated-tax.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
