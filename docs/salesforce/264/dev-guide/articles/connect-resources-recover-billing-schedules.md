---
page_id: connect-resources-recover-billing-schedules
title: Billing Schedule Recovery List (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-recover-billing-schedules.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_recover_billing_schedules.htm
fetched_at: 2026-11-25
---

# Billing Schedule Recovery List (POST)

Recover the latest generated invoice associated with the billing schedules in the `Error` or `Processing` status.

Billing schedules include critical details such as the amount to be billed, next billing date, and status. An invoice can be associated with one or more billing schedules. When an invoice is generated or posted, the billing schedules are updated to reflect the accurate state of the invoice. The billing schedules associated with an invoice are marked in the `Error` status if any of the invoicing processes have errors. Use this API to recover the invoice associated with the billing schedules in the `Error` or `Processing` status.

## Special Access Rules

You need the Manage Errors Using Invoice Error Recovery API permission set to use this API.

## Resource

```
/commerce/invoicing/billing-schedules/collection/actions/recover
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/commerce/invoicing/billing-schedules/collection/actions/recover
```

## Available Version

62.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
  {
    "billingScheduleIds": ["44bDU00000000XXYAY"]
  }
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billing​Schedule​Ids` | String[] | IDs of the billing schedules to recover the invoice for. You can recover one billing schedule per API request. | Required | 62.0 |

## Response Body for POST

[Billing Schedule Recovery List](./connect-responses-billing-schedule-recovery-list-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-recover-billing-schedules.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
