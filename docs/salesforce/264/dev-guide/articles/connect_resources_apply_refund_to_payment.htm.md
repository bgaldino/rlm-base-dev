---
page_id: connect_resources_apply_refund_to_payment.htm
title: Refund Line Apply (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_apply_refund_to_payment.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-11-23
---

# Refund Line Apply (POST)

Make a refund transaction against a payment.

## Resource

```
/commerce/billing/refunds/refundId/actions/apply
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/commerce/billing/refunds/0cbVc0000000G4nIAE/actions/apply
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

[Refund Line Apply](./connect_responses_refund_line_apply_output.htm.md "Output representation of the details of an applied refund. This representation includes the properties of a refund line, such as the date when the refund is applied against a payment and ID of the refund line record.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_apply_refund_to_payment.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
