---
page_id: connect-responses-suspend-resume-billing-output
title: Suspend Resume Billing
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-suspend-resume-billing-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_suspend_resume_billing_output.htm
fetched_at: 2026-11-25
---

# Suspend Resume Billing

Output representation of the list of accounts and billing schedule groups, which are suspended or resumed for billing operations.

## JSON Example

```
{
    "result":{
        {
            "referenceId": "001DU000001o2UwYAI",
            "success": true,
            "errorcode": null,
            "errorMessage":null
        },
        {
            "referenceId": "001DU000001o2UuYAI",
            "success": false,
            "errorcode": "INVALID_API_INPUT",
            "errorMessage":"Billing is already suspended for 9Wsxx000000006TCAQ."
        }
    }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `result` | [Suspend Resume Billing Object](./connect-responses-suspend-resume-billing-entity-output.md)[] | Details of the accounts or billing schedule groups that the suspend or resume billing request is initiated for. | Big, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-suspend-resume-billing-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
