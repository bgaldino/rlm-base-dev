---
page_id: connect-responses-procedure-plan-generic-output
title: Procedure Plan Generic
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-procedure-plan-generic-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-responses
legacy_page_id: connect_responses_procedure_plan_generic_output.htm
fetched_at: 2026-11-25
---

# Procedure Plan Generic

Output representation of the details of the created procedure plan definition record.

## JSON Example

This example shows a sample response of the details of a procedure plan definition record, created by using the Procedure Plan Definitions (POST) API.

```
  {
   "isSuccess":true,
   "recordId":"1FNDU00000000EX4AY"
  }
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | [Procedure Plan Generic Error](./connect-responses-procedure-plan-generic-error.md)[] | Details of the error encountered during the processing of the API request. | Small, 62.0 | 62.0 |
| `isSuccess` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `recordId` | String | ID of the created procedure plan definition record. | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-procedure-plan-generic-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
