---
page_id: connect_responses_write_off_posted_invoice_output_error.htm
title: Posted Invoice Write-Off Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_write_off_posted_invoice_output_error.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Posted Invoice Write-Off Error

Output representation of the error response that's associated with a request to write off a posted invoice.

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

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_write_off_posted_invoice_output_error.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
