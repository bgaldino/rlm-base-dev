---
page_id: connect_resources_rules_application.htm
title: Rules Application (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_rules_application.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-11-23
---

# Rules Application (POST)

Apply payments and credits to an account's invoices based on specified rules defined on the Billing Settings page.

This API uses predefined logic to allocate payments and credits, reducing any manual intervention and errors.

## Resource

```
/revenue/billing/transactions/actions/apply
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/revenue/billing/transactions/actions/apply
```

## Available Version

66.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
  "accountId": "001xx000003DGbQAAW",
  "targetDate": "2024-01-15"
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `accountId` | String | ID of the account to perform the settlement of payments and credits against invoices in adherence with the applied rules. | Required | 66.0 |
| `targetDate` | String | The date used to select invoices and invoice lines with a posted date equal to or later than the target date to apply payments and credits. | Optional | 66.0 |

## Response Body for POST

[Rules Application](./connect_responses_rules_application_output.htm.md "Output representation of the details of rules application.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_rules_application.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
