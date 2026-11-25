---
page_id: connect-responses-credit-memo-apply-list-output
title: Credit Memo Apply List
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-credit-memo-apply-list-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_credit_memo_apply_list_output.htm
fetched_at: 2026-11-25
---

# Credit Memo Apply List

Output representation of the list of applied credit memo results.

## JSON Example

```
{
  "applyCreditResults" : [ {
    "appliedToId" : "3ttxx000000003FAAQ",
    "errors" : null,
    "id" : "4sFxx00000002ppEAA",
    "success" : true
  }, {
    "appliedToId" : "3ttxx0000000001AAA",
    "errors" : null,
    "id" : "4sFxx00000002pqEAA",
    "success" : true
  } ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `applyCredit​Results` | [Credit Memo Apply](./connect-responses-credit-memo-apply-output.md)[] | Output list of the applied credit memo results. | Big, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-credit-memo-apply-list-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
