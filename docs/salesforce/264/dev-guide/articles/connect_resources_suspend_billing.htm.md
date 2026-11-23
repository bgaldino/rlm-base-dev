---
page_id: connect_resources_suspend_billing.htm
title: Suspend Billing (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_suspend_billing.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-11-23
---

# Suspend Billing (POST)

Suspend billing for billing schedule groups or an account for a predefined period.

## Resource

```
/commerce/invoicing/actions/suspend-billing
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/commerce/invoicing/actions/suspend-billing
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
| `referenceIds` | [Suspend Billing Object Input](./connect_requests_suspend_billing_entity_input.htm.md "Input representation of the details such as the ID of the account or billing schedule group along with the effective dates. These details are used to suspend the billing operation.")[] | Input representation of the account or billing schedule group IDs to suspend the billing operation for. | Required | 63.0 |

## Response Body for POST

[Suspend Resume Billing](./connect_responses_suspend_resume_billing_output.htm.md "Output representation of the list of accounts and billing schedule groups, which are suspended or resumed for billing operations.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_suspend_billing.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
