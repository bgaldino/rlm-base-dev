---
page_id: connect_responses_credit_memo_unapply_output.htm
title: Credit Memo Unapply
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_credit_memo_unapply_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Credit Memo Unapply

Output representation of the details of the credit memo invoice application record with the status of the request.

## JSON Example

```
{
    "errors": [],
    "id": "4sFxx00000002ppEAA",
    "success": true
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Error Response](https://developer.salesforce.com/docs/atlas.en-us.264.0.chatterapi.meta/chatterapi/connect_responses_error_response.htm "HTML (New Window)") | List of errors encountered during the processing of the API request. | Big, 62.0 | 62.0 |
| `id` | String | ID of the credit memo invoice application record. | Small, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the credit memo is successfully unapplied (`true`) or not (`false`). | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_credit_memo_unapply_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
