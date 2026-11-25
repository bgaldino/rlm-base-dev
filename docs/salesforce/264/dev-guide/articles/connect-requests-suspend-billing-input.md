---
page_id: connect-requests-suspend-billing-input
title: Suspend Billing Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-suspend-billing-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_suspend_billing_input.htm
fetched_at: 2026-11-25
---

# Suspend Billing Input

Input representation of the details of the request to suspend the billing operation for an account or a billing schedule group.

## JSON Example

```
{
    "referenceIds": 
    [
        {
            "referenceId": "001DU000001o2UwYAI",
            "suspendDate": "2024-11-27",
            "resumeDate": "2024-12-27"
        }
    ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `referenceIds` | [Suspend Billing Object Input](./connect-requests-suspend-billing-entity-input.md)[] | Input representation of the account or billing schedule group IDs to suspend the billing operation for. | Required | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-suspend-billing-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
