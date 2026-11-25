---
page_id: connect-requests-draft-to-posted-invoice-input
title: Invoice Draft To Posted Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-draft-to-posted-invoice-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_draft_to_posted_invoice_input.htm
fetched_at: 2026-11-25
---

# Invoice Draft To Posted Input

Input representation of the details of the draft invoice that’s posted.

## JSON Example

```
{
  "invoiceIds": ["3ttxx0000004CIjAAM"]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `correlationId` | String | Splunk correlation ID to track the messages that are related to the request and are logged in Splunk by the different services involved in the request. If the ID isn’t specified, the service creates a random Universally Unique Identifier (UUID). | Optional | 62.0 |
| `invoiceIds` | String[] | IDs of the invoice records in `Draft` status to be posted. You can post one draft invoice per API request. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-draft-to-posted-invoice-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
