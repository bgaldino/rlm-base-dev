---
page_id: connect-responses-rules-application-error-output
title: Rules Application Error
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-rules-application-error-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_rules_application_error_output.htm
fetched_at: 2026-11-25
---

# Rules Application Error

Output representation of the error details for rules application failure.

## JSON Example

This example shows the rules application error.

```
{
  "errors": [
    {
      "errorCode": "INVALID_ACCOUNT",
      "message": "The specified account does not exist or is not accessible."
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Code that indicates the type of error. | Big, 66.0 | 66.0 |
| `message` | String | Message that states the reason for error, if any. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-rules-application-error-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
