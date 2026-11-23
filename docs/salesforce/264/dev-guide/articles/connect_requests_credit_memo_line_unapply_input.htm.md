---
page_id: connect_requests_credit_memo_line_unapply_input.htm
title: Credit Memo Line Unapply Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_credit_memo_line_unapply_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-11-23
---

# Credit Memo Line Unapply Input

Input representation of the details of the request to unapply a credit memo line from an invoice line.

## JSON Example

```
{
 "description": "Unapply a credit memo line from invoice line 1",
 "effectiveDate": "2024-07-01"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `description` | String | Explanation or reason for unapplying the credit memo line. | Optional | 62.0 |
| `effectiveDate` | String | Effective date for the credit memo line. | Optional | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_credit_memo_line_unapply_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
