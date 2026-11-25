---
page_id: connect-responses-refund-line-apply-output
title: Refund Line Applied Response
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-refund-line-apply-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_refund_line_apply_output.htm
fetched_at: 2026-11-25
---

# Refund Line Applied Response

Output representation of the details of an applied refund. This representation includes the properties of a refund line, such as the date when the refund is applied against a payment and ID of the refund line record.

## JSON Example

```
{
  "appliedDate": "2020-08-11T08:09:01.000Z",
  "id": "0dRR000000000CsMAI"
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `appliedDate` | String | Date when the refund is applied against a payment. | Big, 64.0 | 64.0 |
| `id` | String | ID of the refund line record. | Big, 64.0 | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-refund-line-apply-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
