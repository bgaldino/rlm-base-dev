---
page_id: connect-resources-suspend-billing
title: Suspend Billing (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-suspend-billing.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_suspend_billing.htm
fetched_at: 2026-11-25
---

# Suspend Billing (POST)

Suspend billing for billing schedule groups or an account for a predefined period.

## Resource

```
/commerce/invoicing/actions/suspend-billing
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/commerce/invoicing/actions/suspend-billing
```

## Available Version

63.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

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

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `referenceIds` | [Suspend Billing Object Input](./connect-requests-suspend-billing-entity-input.md)[] | Input representation of the account or billing schedule group IDs to suspend the billing operation for. | Required | 63.0 |

## Response Body for POST

[Suspend Resume Billing](./connect-responses-suspend-resume-billing-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-suspend-billing.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
