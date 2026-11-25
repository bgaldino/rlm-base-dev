---
page_id: connect-resources-draft-to-posted-invoice
title: Invoice Draft to Posted Status (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-draft-to-posted-invoice.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_draft_to_posted_invoice.htm
fetched_at: 2026-11-25
---

# Invoice Draft to Posted Status (POST)

Update the status of the invoice from Draft to Posted.

This API calls an external tax engine or provides information to your tax adapter implementation to calculate taxes for the draft invoice, post the invoice, and update the related billing schedules and billing periods.

## Special Access Rules

You need the Billing Operations User permission set to use this API.

## Resource

```
/commerce/invoicing/invoices/collection/actions/post
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/commerce/invoicing/invoices/collection/actions/post
```

## Available Version

62.0

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
| `correlationId` | String | Splunk correlation ID to track the messages that are related to the request and are logged in Splunk by the different services involved in the request. If the ID isn’t specified, the service creates a random Universally Unique Identifier (UUID). | Optional | 62.0 |
| `invoiceIds` | String[] | IDs of the invoice records in `Draft` status to be posted. You can post one draft invoice per API request. | Required | 62.0 |

## Response Body for POST

[Revenue Async Response](./connect-responses-revenue-async-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-draft-to-posted-invoice.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
