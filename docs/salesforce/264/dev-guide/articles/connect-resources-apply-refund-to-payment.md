---
page_id: connect-resources-apply-refund-to-payment
title: Refund Line Apply (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-apply-refund-to-payment.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_apply_refund_to_payment.htm
fetched_at: 2026-11-25
---

# Refund Line Apply (POST)

Make a refund transaction against a payment.

## Resource

```
/commerce/billing/refunds/{refundId}/actions/apply
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/commerce/billing/refunds/{0cbVc0000000G4nIAE}/actions/apply
```

## Available Version

64.0

## HTTP Methods

POST

## Path Parameter for POST

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `refundId` | String | ID of the refund record. | Required | 64.0 |

## Request Body for POST

**JSON Example**

```
{
  "appliedToId": "0aQR00000004ZkKMAU",
  "amount": 10,
  "effectiveDate": "2020-08-11T07:53:15.000Z",
  "comments": "Payment application."
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `amount` | Double | Amount to refund. | Required | 64.0 |
| `appliedToId` | String | ID of a payment or credit memo record. The refund is applied to this object. | Required | 64.0 |
| `comments` | String | Additional details of the refund request. | Optional | 64.0 |
| `effectiveDate` | String | Date from when the refund is in effect. | Optional | 64.0 |

## Response Body for POST

[Refund Line Apply](./connect-responses-refund-line-apply-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-apply-refund-to-payment.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
