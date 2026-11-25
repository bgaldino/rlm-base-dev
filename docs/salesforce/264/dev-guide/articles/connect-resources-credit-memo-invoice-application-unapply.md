---
page_id: connect-resources-credit-memo-invoice-application-unapply
title: Unapply Credit Memo (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-credit-memo-invoice-application-unapply.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_credit_memo_invoice_application_unapply.htm
fetched_at: 2026-11-25
---

# Unapply Credit Memo (POST)

Unapply a credit memo from an invoice and return the invoice and the credit memo to their pre-application states.

Use this resource if an error occurred when a credit is issued. For example, if an incorrect credit memo is applied to an invoice, or if a credit memo is created for an incorrect amount, use this resource to unapply the credit memo.

## Special Access Rules

You need the Credit Memo Operations User permission set to use this API.

## Resource

```
/commerce/invoicing/credit-memo-inv-applications/{creditMemoInvApplicationId}/actions/unapply
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/commerce/invoicing/credit-memo-inv-applications/{4sFSG000002nxPB2AY}/actions/unapply
```

## Available Version

62.0

## HTTP Methods

POST

## Path Parameter for POST

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `creditMemo​InvApplication​Id` | String | ID of the credit memo invoice application. | Required | 62.0 |

## Request Body for POST

**JSON Example**

```
    {
      "description": "Unapply credit memo from invoice to revert an error",
      "effectiveDate": "2024-07-01"
    }
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `description` | String | Explanation or reason for unapplying the credit memo. | Optional | 62.0 |
| `effectiveDate` | String | Effective date for the credit memo. | Optional | 62.0 |

## Response Body for POST

[Credit Memo Unapply](./connect-responses-credit-memo-unapply-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-credit-memo-invoice-application-unapply.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
