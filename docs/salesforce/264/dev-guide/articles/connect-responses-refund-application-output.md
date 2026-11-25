---
page_id: connect-responses-refund-application-output
title: Refund Application
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-refund-application-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: connect-responses-refund-credit-memo-output
legacy_page_id: connect_responses_refund_application_output.htm
fetched_at: 2026-11-25
---

# Refund Application

Output representation of a single refund application record created by the refund against a credit memo API.

## JSON Example

```
{
  "applicationId": "4sFxx00000002ppEAA",
  "appliedToId": "a1Yxx0000004C95"
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `application​Id` | String | ID of the created application junction entity (`CreditMemoRefund` or `CreditMemoLineRefund`). | Big, 68.0 | 68.0 |
| `applied​To​Id` | String | ID of the record that the refund was applied to (the credit memo or a credit memo line). | Big, 68.0 | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-refund-application-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
