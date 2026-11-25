---
page_id: connect-responses-write-off-posted-invoice-output-error
title: Posted Invoice Write-Off Error
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-write-off-posted-invoice-output-error.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_write_off_posted_invoice_output_error.htm
fetched_at: 2026-11-25
---

# Posted Invoice Write-Off Error

Output representation of the error response that’s associated with a request to write off a posted invoice.

## JSON Example

```
{
  "errors": {
    "errorcode": "INVALID_API_INPUT",
    "errorMessage": "Reason is missing"
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Code that represents the error. | Small, 64.0 | 64.0 |
| `error​Message` | String | Message that describes the error. | Small, 64.0 | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-write-off-posted-invoice-output-error.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
