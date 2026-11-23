---
page_id: connect_responses_preview_approval_error.htm
title: Preview Approval Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_preview_approval_error.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Advanced Approvals
parent_page: advanced_approvals_api_responses.htm
fetched_at: 2026-11-23
---

# Preview Approval Error

Output representation of the error details associated with the Preview Approval API.

## JSON Example

This example shows a sample error scenario.

```
{
  "approvalChainItems": [],
  "error": {
    "correlationId": "0Q0DU0000005HZC0A2",
    "errorCode": "[xmlrpc=-1, statusCode=INVALID_API_INPUT, exceptionCode=null, scope=PublicApi, http=400]",
    "errorMessage": "Looks like the flow associated with this approval workflow for the current record isn't active. Activate the flow and try again.",
    "source": "PreviewApprovalDataProcessingException"
  },
  "status": "Failure"
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `correlationId` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Small, 65.0 | 65.0 |
| `errorCode` | String | Code for the resultant error. | Small, 65.0 | 65.0 |
| `errorMessage` | String | Error message for the resultant error. | Small, 65.0 | 65.0 |
| `source` | String | Details about the source of the error. | Small, 65.0 | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_preview_approval_error.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
