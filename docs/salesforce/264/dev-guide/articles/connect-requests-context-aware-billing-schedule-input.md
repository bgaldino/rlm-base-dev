---
page_id: connect-requests-context-aware-billing-schedule-input
title: Context-Aware Billing Schedule
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-context-aware-billing-schedule-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_context_aware_billing_schedule_input.htm
fetched_at: 2026-11-25
---

# Context-Aware Billing Schedule

Input representation of the billing transaction details.

## JSON Example

```
{
    "billingTransactionIds": [ "801xx000003H1H9AAK"]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billing​Transaction​Ids` | String[] | ID of the billing transaction. This property value is the ID of the order if the source of the billing request is for the Order object. If the order product associated with the specified order ID doesn’t have an associated billing treatment ID, the API considers the default billing treatment ID. The generated billing schedule group has the default billing treatment ID. The API supports only one billing transaction ID in the input. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-context-aware-billing-schedule-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
