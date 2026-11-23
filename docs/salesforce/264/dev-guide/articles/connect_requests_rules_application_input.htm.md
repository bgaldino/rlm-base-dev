---
page_id: connect_requests_rules_application_input.htm
title: Rules Application Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_rules_application_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-11-23
---

# Rules Application Input

Input representation for applying payments and credits to invoices based on rules.

## JSON Example

```
{
  "accountId": "001xx000003DGbQAAW",
  "targetDate": "2024-01-15"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `accountId` | String | ID of the account to perform the settlement of payments and credits against invoices in adherence with the applied rules. | Required | 66.0 |
| `targetDate` | String | The date used to select invoices and invoice lines with a posted date equal to or later than the target date to apply payments and credits. | Optional | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_rules_application_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
