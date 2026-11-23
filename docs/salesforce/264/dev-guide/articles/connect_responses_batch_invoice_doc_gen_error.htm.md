---
page_id: connect_responses_batch_invoice_doc_gen_error.htm
title: Error Response for Batch Invoice Document Generation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_batch_invoice_doc_gen_error.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Error Response for Batch Invoice Document Generation

Output representation of the error details associated with the Batch Invoice Document Generation API.

## JSON Example

```
  "errors": {
    "errorCode": "API_DISABLED_FOR_ORG",
    "message": "Document Generation is not enabled for this org!"
  }
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Code for the resultant error. | Big, 63.0 | 63.0 |
| `errorMessage` | String | Error message for the resultant error. | Big, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_batch_invoice_doc_gen_error.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
