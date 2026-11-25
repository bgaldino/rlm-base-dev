---
page_id: connect-resources-convert-negative-invoice-lines-to-credit
title: Negative Invoice Lines to Credit Conversion (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-convert-negative-invoice-lines-to-credit.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_convert_negative_invoice_lines_to_credit.htm
fetched_at: 2026-11-25
---

# Negative Invoice Lines to Credit Conversion (POST)

Convert a list of invoice lines with a negative amount into a posted credit memo. This conversion is applicable for a single invoice at a time.

Keep these considerations in mind when you use this API.

- All invoice lines must be related to the same invoice.

- The invoice line must have a negative amount.

- The invoice line must not be a previously converted credit memo.

- The invoice must have the `Posted` status.

- The invoice must not have any active settlements such as credit applications.

## Special Access Rules

You need the Credit Memo Operations User permission set to use this API.

## Resource

```
/commerce/invoicing/invoices/{invoiceId}/actions/convert-to-credit
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/commerce/invoicing/invoices/{3ttxx00000000XtAAI}/actions/convert-to-credit
```

## Available Version

62.0

## HTTP Methods

POST

## Path Parameter for POST

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `invoiceId` | String | ID of the invoice whose negative invoice lines must be converted into a posted credit memo. | Required | 62.0 |

## Request Body for POST

**JSON Example**

```
  {
  "invoiceLines": ["5TVxx0000004C92GAE", "5TVxx0000004C93GAE"],
  "description": "Convert negative invoice lines into credit",
  "effectiveDate":"2022-05-18"
  }
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `description` | String | Description stamped on the credit memo that’s created after the negative invoice line conversion. | Optional | 62.0 |
| `effectiveDate` | String | Date stamped on the credit memo that’s created after the negative invoice line conversion. | Required | 62.0 |
| `invoiceLines` | String[] | Complete list of the negative invoice lines along with the associated invoice line taxes. The specified negative invoice lines are converted into a posted credit memo. | Optional | 62.0 |

## Response Body for POST

[Convert Negative Invoice Lines](./connect-responses-convert-negative-invoice-lines-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-convert-negative-invoice-lines-to-credit.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
