---
page_id: connect_resources_credit_memo_line_level_apply.htm
title: Apply Credit Memo Line (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_credit_memo_line_level_apply.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-11-23
---

# Apply Credit Memo Line (POST)

Adjust or correct already issued invoices by applying an existing credit memo line to an invoice line.

## Special Access Rules

You need the Credit Memo Operations User permission set to use this API.

## Resource

```
/commerce/invoicing/credit-memo-lines/creditMemoLineId/actions/apply
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/commerce/invoicing/credit-memo-lines/9yxSG0000000LUHYA2/actions/apply
```

## Available Version

62.0

## HTTP Methods

POST

## Path Parameter for POST

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `creditMemo​LineId` | String | ID of the credit memo line record. | Required | 62.0 |

## Request Body for POST

**JSON Example**

```
{
 "applyCreditDetails": [
 {
 "invoiceLineId": "5TVSG0000002ZJR4A2",
 "appliedAmount": 5,
 "description": "Apply to invoice line 1",
 "effectiveDate": "2024-07-01"
 },
 {
 "invoiceLineId": "5TVSG0000002ZJS4A2",
 "appliedAmount": 10,
 "description": "Apply to invoice line 2",
 "effectiveDate": "2024-07-01"
 }
 ]
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `applyCredit​Details` | [Credit Memo Line Application Input](./connect_requests_credit_memo_line_application_input.htm.md "Input representation of the request to specify one or more applications to apply a credit memo line for, with each application representing an invoice line.")[] | List of one or more applications to apply the credit memo line for. Each application represents an invoice line that’s credited by using the balance of the specified credit memo line. | Required | 62.0 |

## Response Body for POST

[Credit Memo Line Applied](./connect_responses_credit_memo_line_applied.htm.md "Output representation of the list of applied credit memo line results.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_credit_memo_line_level_apply.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
