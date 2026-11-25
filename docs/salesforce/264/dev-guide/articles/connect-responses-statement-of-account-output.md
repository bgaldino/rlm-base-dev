---
page_id: connect-responses-statement-of-account-output
title: Statement of Account
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-statement-of-account-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_statement_of_account_output.htm
fetched_at: 2026-11-25
---

# Statement of Account

Output representation of the details of the generated account statement with async tracking details.

## JSON Example

This example shows a sample successful response.

```
{
  "requestIdentifier": "a0Bxx000000001ZEAQ",
  "statusURL": "/services/data/v60.0/commerce/billing/document-generation-process/a0Bxx000000001ZEAQ/status",
  "success": true,
  "accountId": "001xx000003DGb2AAG",
  "templateId": "0TRxx000000001XGAQ",
  "errors": null
}
```

This example shows a sample error response.

```
{
  "success": false,
  "errors": [
    {
      "code": "ACCOUNT_NOT_FOUND",
      "message": "Account with ID 001XX000004DKy5YAG not found",
      "field": "accountId"
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `accountId` | String | Primary account ID the statement is generated for. | Big, 66.0 | 66.0 |
| `errors` | [Error Response](./connect-responses-error-response.md)[] | List of errors encountered during the processing of the API request. | Big, 66.0 | 66.0 |
| `requestIdentifier` | String | Unique identifier for the request. | Big, 66.0 | 66.0 |
| `statusURL` | String | Status URL to track the operation. | Big, 66.0 | 66.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Big, 66.0 | 66.0 |
| `templateId` | String | Document template ID that’s used to generate the PDF. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-statement-of-account-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
