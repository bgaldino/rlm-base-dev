---
page_id: connect-responses-billing-arrangement-line
title: Billing Arrangement Line
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-billing-arrangement-line.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_billing_arrangement_line.htm
fetched_at: 2026-11-25
---

# Billing Arrangement Line

Output representation that contains the details of a specific line item within a billing arrangement, defining how charges are split for an account.

## JSON Example

```
{
  "billingArrangementLineId": "1blxx000000006TAAQ",
  "accountId": "accId1",
  "billingAccountId": "bAccId1",
  "isRemainderAdjustmentAccount": false,
  "percentage": 60.00
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `accountId` | String | ID of the account associated with the billing line. | Big, 66.0 | 66.0 |
| `billing​AccountId` | String | ID of the billing account responsible for this portion of the bill. | Big, 66.0 | 66.0 |
| `billingArrangement​LineId` | String | Unique ID of the billing arrangement line. | Big, 66.0 | 66.0 |
| `isRemainder​AdjustmentAccount` | Boolean | Indicates whether the specific line is designated as the adjustment account for any remainder (`true`) or not (`false`). | Big, 66.0 | 66.0 |
| `percentage` | Double | Percentage of the charge allocated to this line. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-billing-arrangement-line.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
