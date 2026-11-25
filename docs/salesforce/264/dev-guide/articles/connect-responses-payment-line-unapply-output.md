---
page_id: connect-responses-payment-line-unapply-output
title: Payment Line Unapply
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-payment-line-unapply-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_payment_line_unapply_output.htm
fetched_at: 2026-11-25
---

# Payment Line Unapply

Output representation of the details of the reversed payment line application. The details include the ID of the payment line record and date when the payment line application was reversed.

## JSON Example

```
{
  "unappliedDate": "2020-08-11T08:09:01.000Z",
  "id": "1PLR000000000dDOAQ"
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the payment line record. | Big, 64.0 | 64.0 |
| `unapplied​Date` | String | Date when the payment line application was reversed. | Big, 64.0 | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-payment-line-unapply-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
